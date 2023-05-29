from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, insert, inspect, or_

from src.db.session import session_scope
from src.models import Base, BaseModel
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import PaginationInput

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SearchOutput = TypeVar("SearchOutput", bound=BaseModel)


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

    def get(self, uid: Any) -> Optional[ModelType]:
        with session_scope() as session:
            stmt = select(self.model).where((self.model.uid == uid) & (self.model.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    # def get_multi_paginated(self, filter_field, pagination: Pagination) -> List[ModelType]:
    #     # return db.query(self.model).offset(skip).limit(limit).all()
    #     model_field = getattr(self.model, filter_field)
    #     with session_scope() as session:
    #         if pagination.search:
    #             return session.query(self.model).where(
    #                 (model_field.ilike(f"%{pagination.search}%")) & (self.model.deleted_at.is_(None))).offset(
    #                 pagination.page).limit(pagination.limit).all()
    #         return session.query(self.model).where(self.model.deleted_at.is_(None)).offset(pagination.page).limit(
    #             pagination.limit).all()

    def get_multi(self) -> List[ModelType]:
        with session_scope() as session:
            result = session.query(self.model).filter(self.model.deleted_at.is_(None)).all()
            return result

    def get_multi_by_attributes(self, field, attrs: List[str]) -> List[ModelType]:
        model_field = getattr(self.model, field)
        with session_scope() as session:
            stmt = session.query(self.model).filter(model_field.in_(attrs) & (self.model.deleted_at.is_(None)))
            return stmt.all()

    def create_or_update(self, input_unique_field, inputs: List[CreateSchemaType], search_node) -> \
            Response[SearchOutput]:
        db_obj_list = []
        with session_scope() as session:
            count = session.query(self.model).count()
            # Check if Db Obj already exist using attr
            existed_db_obj_list = self.get_multi_by_attributes(input_unique_field,
                                                               [getattr(input_obj, input_unique_field) for input_obj in
                                                                inputs if input_obj.uid is None])
            if existed_db_obj_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_db_obj_list,
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
                        db_obj_list.append(db_obj)

                    else:
                        db_obj = next(filter(lambda db_obj: str(db_obj.uid) == str(input1.uid), existed_db_objs), None)
                        if db_obj:
                            obj_data = jsonable_encoder(input1)
                            obj_data.pop("uid")
                            for key, value in obj_data.items():
                                setattr(db_obj, key, value)
                            db_obj_list.append(db_obj)
                session.add_all(db_obj_list)
                session.commit()
                return Response(status=True, code=ResponseCode.SUCCESS, data=db_obj_list,
                                message="Successfully Submitted")
            except Exception as e:
                print(e)
                return Response(status=False, code=ResponseCode.SUCCESS,
                                data=search_node(items=db_obj_list, total_count=count),
                                message="Failed to Submit")

    @staticmethod
    def update(db_obj: ModelType,
               input_obj: UpdateSchemaType
               ) -> ModelType:
        with session_scope() as session:
            obj_data = jsonable_encoder(db_obj)
            for key, value in input_obj.items():
                setattr(obj_data, key, value)
            session.add(obj_data)
            session.commit()
            session.refresh(obj_data)
            return obj_data

    def remove(self, uid: str) -> ModelType:
        with session_scope() as session:
            obj = session.query(self.model).filter_by(uid=uid).update({self.model.deleted_at: pendulum.now()})
            session.commit()
            return obj

    def get_multi_paginated(self, pagination: PaginationInput, search_columns: List[str], search_node) -> SearchOutput:
        with session_scope() as session:
            query = session.query(self.model).filter(self.model.deleted_at.is_(None))
            total_count = query.count()
            search_q = pagination.search if pagination.search else ''
            # Apply filters
            filter_conditions = []
            for column in inspect(self.model).columns:
                if column.name in search_columns:
                    filter_conditions.append(getattr(self.model, column.name).ilike(f"%{search_q}%"))
            if filter_conditions:
                query = query.filter(or_(*filter_conditions))
            # Apply pagination
            query = query.limit(pagination.limit).offset(pagination.offset)

            # Fetch items and total count
            items = query.all()
            session.close()

            return search_node(items=items, total_count=total_count)
