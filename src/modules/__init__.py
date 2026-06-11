from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, insert, inspect, or_, and_, cast, String
from sqlalchemy.orm import joinedload

from src.core.security import Info
from src.database.session import session_scope
from src.models import Base, BaseModel
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import PaginationInput

ModelType = TypeVar("ModelType", bound=Base)
RelatedModelType = TypeVar("RelatedModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SearchOutput = TypeVar("SearchOutput", bound=BaseModel)


# unique search columns


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic/SQlAlchemy model (schema) class
        """
        self.model = model
        self.session = session_scope()

    def _get_user_id(self, info: Optional[Info]) -> Optional[int]:
        """Extract user ID from Strawberry context (current_user.id)."""
        if info is None:
            return None
        try:
            current_user = info.context.current_user
            if current_user:
                # Try id first, then fallback to uid/guid
                return current_user.id or current_user.uid or current_user.guid
        except Exception:
            return None
        return None

    def get(self, uid: Any) -> Optional[ModelType]:
        if uid == '':
            uid = None
        with session_scope() as session:
            stmt = select(self.model).where((self.model.uid == uid) & (self.model.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def get_multi(self) -> List[ModelType]:
        with session_scope() as session:
            result = session.query(self.model).filter(self.model.deleted_at.is_(None)).all()
            return result

    def get_multi_by_attributes(self, field, attrs: List[str]) -> List[ModelType]:
        model_field = getattr(self.model, field)
        with session_scope() as session:
            stmt = session.query(self.model).filter(model_field.in_(attrs) & (self.model.deleted_at.is_(None)))
            return stmt.all()

    def create_or_update(self, input_unique_field, inputs: List[CreateSchemaType], search_node,
                          info: Optional[Info] = None) -> Response[SearchOutput]:
        db_obj_list = []
        user_id = self._get_user_id(info)

        with session_scope() as session:
            count = session.query(self.model).count()
            # Check if Db Obj already exist using attr
            existed_db_obj_list = self.get_multi_by_attributes(input_unique_field,
                                                               [getattr(input_obj, input_unique_field) for input_obj in
                                                                inputs if input_obj.uid is None])
            if existed_db_obj_list:
                return Response(status=False, code=ResponseCode.DUPLICATE,
                                data=search_node(items=db_obj_list, total_count=count),
                                message="Entry Already exists")
            try:
                # check for existing Db Objs using uid
                existed_db_objs = self.get_multi_by_attributes('uid', [input.uid for input in inputs])
                # create new Db Objs
                for input1 in inputs:
                    if input1.uid is None:
                        obj_in_data = jsonable_encoder(input1)
                        obj_in_data.pop("uid")
                        db_obj = self.model(**obj_in_data)  # type: ignore
                        # Set created_by for new records
                        if user_id and hasattr(db_obj, 'created_by'):
                            db_obj.created_by = user_id
                        db_obj_list.append(db_obj)

                    else:
                        db_obj = next(filter(lambda db_obj: str(db_obj.uid) == str(input1.uid), existed_db_objs), None)
                        if db_obj:
                            obj_data = jsonable_encoder(input1)
                            obj_data.pop("uid")
                            for key, value in obj_data.items():
                                setattr(db_obj, key, value)
                            # Set updated_by for existing records
                            if user_id and hasattr(db_obj, 'updated_by'):
                                db_obj.updated_by = user_id
                            db_obj_list.append(db_obj)
                session.add_all(db_obj_list)
                session.commit()
                return Response(status=True, code=ResponseCode.SUCCESS,
                                data=search_node(items=db_obj_list, total_count=count),
                                message="Successfully Submitted")
            except Exception as e:
                print(e)
                return Response(status=False, code=ResponseCode.SUCCESS,
                                data=search_node(items=db_obj_list, total_count=count),
                                message="Failed to Submit")

    @staticmethod
    def update(db_obj: ModelType,
               input_obj: UpdateSchemaType,
               info: Optional[Info] = None
               ) -> ModelType:
        with session_scope() as session:
            obj_data = jsonable_encoder(db_obj)
            for key, value in input_obj.items():
                setattr(obj_data, key, value)
            # Set updated_by if user context available
            if info:
                try:
                    current_user = info.context.current_user
                    if current_user and hasattr(obj_data, 'updated_by'):
                        user_id = current_user.id or current_user.uid or current_user.guid
                        obj_data.updated_by = user_id
                except Exception:
                    pass
            session.add(obj_data)
            session.commit()
            session.refresh(obj_data)
            return obj_data

    def remove(self, uid: str,
               info: Optional[Info] = None) -> ModelType:
        with session_scope() as session:
            obj = session.query(self.model).filter_by(uid=uid)
            if not obj.first():
                msg = "%s object not found with uid %s" % (self.model, uid)
                raise Exception(msg)
            update_data = {self.model.deleted_at: pendulum.now()}
            # Set deleted_by if user context available
            if info:
                try:
                    current_user = info.context.current_user
                    if current_user:
                        user_id = current_user.id or current_user.uid or current_user.guid
                        if user_id:
                            update_data[self.model.deleted_by] = user_id
                except Exception:
                    pass
            obj.update(update_data)
            session.commit()
            return obj

    def remove_check_relations(self, uid: str, parent_id, child_models: List[RelatedModelType],
                                info: Info) -> ModelType:
        with session_scope() as session:
            """
            Remove object by restriction on related tables if has entries
            """
            obj = session.query(self.model).filter_by(uid=uid)
            if not obj.first():
                msg = "Provided Entry not found!"
                raise ValueError(msg)
            child_entries_exist = False
            for child_table in child_models:
                model_field = getattr(child_table, parent_id)
                child_entries = session.query(child_table).filter(model_field == obj.first().id).all()
                if child_entries:
                    child_entries_exist = True
                    break

            if child_entries_exist:
                msg = "Cannot delete. Entry in use."
                raise ValueError(msg)

            # Set deleted_by from current user context
            user_id = None
            try:
                current_user = info.context.current_user
                if current_user:
                    user_id = current_user.id or current_user.uid or current_user.guid
            except Exception:
                pass

            update_data = {self.model.deleted_at: pendulum.now()}
            if user_id:
                update_data[self.model.deleted_by] = user_id
            obj.update(update_data)
            session.commit()
            return obj

    def get_multi_paginated(self, pagination: PaginationInput, search_columns: List[str], search_node,
                            relationships_to_join: List[str] = None, unique_search: List[dict] = None) -> SearchOutput:
        with session_scope() as session:
            query = session.query(self.model).filter(self.model.deleted_at.is_(None))
            search_q = pagination.search if pagination.search else ''

            # filter condition if specified unique column
            unique_filter_conditions = []
            if unique_search:
                for condition in unique_search:
                    for column, value in condition.items():
                        unique_filter_conditions.append(getattr(self.model, column) == value)
            if unique_filter_conditions:
                query = query.filter(and_(*unique_filter_conditions))

            # Apply filters
            filter_conditions = []
            for column in inspect(self.model).columns:
                if column.name in search_columns:
                    filter_conditions.append(cast(getattr(self.model, column.name), String).ilike(f"%{str(search_q)}%"))

            if filter_conditions:
                query = query.filter(or_(*filter_conditions))

            total_count = query.count()

            # Apply pagination
            query = query.limit(pagination.limit).offset(pagination.offset * pagination.limit)
            # Fetch items and total count
            if relationships_to_join and len(relationships_to_join) > 0:
                for relationship_name in relationships_to_join:
                    query = query.options(joinedload(relationship_name))
            items = query.all()
            session.close()

            return search_node(items=items, total_count=total_count)