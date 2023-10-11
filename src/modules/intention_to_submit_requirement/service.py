import uuid
from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc

from src.db.session import session_scope
from src.models.intention_to_submit_requirement import IntentionToSubmitRequirement
from src.modules.program_category.service import ProgramCategoryService
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import IntentionToSubmitRequirementNode, IntentionToSubmitRequirementInput, \
    IntentionToSubmitRequirementListNode


class IntentionToSubmitRequirementService(
    CRUDBase[IntentionToSubmitRequirement, IntentionToSubmitRequirementInput, IntentionToSubmitRequirementNode]):
    @staticmethod
    def get_intention_to_submit_requirement() -> List[IntentionToSubmitRequirement]:
        with session_scope() as session:
            result = session.query(IntentionToSubmitRequirement).order_by(
                desc(IntentionToSubmitRequirement.updated_at)).all()
            return result

    @staticmethod
    def get_intention_to_submit_requirement_by_category(category_uid: str) -> Response[List[IntentionToSubmitRequirementNode]]:

        """
        Get get_intention_to_submit_requirement by names
        :return:
        """

        with session_scope() as session:
            # Verify and get supplied program uid. and get existed year id from returned Program model
            try:
                program_category_id = ProgramCategoryService.get_program_category_by_uid(category_uid).id
            except Exception as e:
                print(e)
                print(category_uid)
                return Response(status=False, code=ResponseCode.FAILURE,
                                data=IntentionToSubmitRequirementNode,
                                message="You have submitted incorrect program category details")

            stmt = select(IntentionToSubmitRequirement).where(
                (IntentionToSubmitRequirement.program_category_id == program_category_id)
                & (IntentionToSubmitRequirement.deleted_at.is_(None))).order_by(
                desc(IntentionToSubmitRequirement.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_intention_to_submit_requirement_by_uids(uids: List[str]) -> List[IntentionToSubmitRequirement]:
        """
        Get Seminar Types by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(IntentionToSubmitRequirement).where((IntentionToSubmitRequirement.uid.in_(uids))
                                                              & (IntentionToSubmitRequirement.deleted_at.is_(
                None))).order_by(desc(IntentionToSubmitRequirement.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_intention_to_submit_requirement_by_uid(uid: str) -> IntentionToSubmitRequirement | None:
        """
        Get Intention To Submit Requirement by uid
        :param uid:
        :return:
        """
        try:
            # Convert the input UID string to a UUID object
            uid_uuid = uuid.UUID(uid)
        except ValueError:
            # Handle the case when the input UID is not a valid UUID
            return None

        with session_scope() as session:
            stmt = select(IntentionToSubmitRequirement).where(
                (IntentionToSubmitRequirement.uid == uid_uuid) & (IntentionToSubmitRequirement.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_get_intention_to_submit_requirement(self, inputs: List[IntentionToSubmitRequirementInput]) \
            -> Response[IntentionToSubmitRequirementNode]:
        """
        Register Intention To Submit Requirement
        :param inputs:
        :return:
        """
        print("Here")
        intention_to_submit_requirement_list = []
        action_name = "Register"
        with session_scope() as session:
            # check for existing intention to submit requirement using uid
            existed_course_category = self.get_intention_to_submit_requirement_by_uids(
                [inputItem.uid for inputItem in inputs])

            for inputItem in inputs:
                if inputItem.uid is None:
                    # Check if the program Category Exist

                    try:
                        program_category = ProgramCategoryService.get_program_category_by_uid(
                            inputItem.program_category_uid)

                        if program_category is None:
                            raise ValueError("You have submitted incorrect programs category details")
                    except Exception as e:
                        print(e)
                        return Response(status=False, code=ResponseCode.FAILURE,
                                        data=IntentionToSubmitRequirementListNode(items=[], total_count=0),
                                        message="You have submitted incorrect program category details")

                    # Check if the Category exist
                    print(inputItem.program_category_uid)
                    existed_intention_to_submit_requirement_list = self.get_intention_to_submit_requirement_by_category(
                        inputItem.program_category_uid)

                    if existed_intention_to_submit_requirement_list:
                        return Response(status=False, code=ResponseCode.DUPLICATE,
                                        data=IntentionToSubmitRequirementNode,
                                        message="Intention To Submit Requirement Already Exists")
                    intention_to_submit_requirements = IntentionToSubmitRequirement(
                        minimum_seminars=inputItem.minimum_seminars,
                        minimum_manuscripts=inputItem.minimum_manuscripts,
                        life_span=inputItem.life_span,
                        seminar_pass_marks=inputItem.seminar_pass_marks,
                        # program_category_uid=inputItem.program_category_uid,
                        program_category=program_category
                    )
                    intention_to_submit_requirement_list.append(intention_to_submit_requirements)
                else:
                    action_name = "Update"
                    intention_to_submit_requirements = next(
                        filter(
                            lambda intention_to_submit_requirements: str(intention_to_submit_requirements.uid) == str(
                                inputItem.uid),
                            existed_course_category), None)
                    if intention_to_submit_requirements:
                        obj_data = jsonable_encoder(inputItem)
                        for key, value in obj_data.items():
                            setattr(intention_to_submit_requirements, key, value)
                        intention_to_submit_requirement_list.append(intention_to_submit_requirements)
            session.add_all(intention_to_submit_requirement_list)
            count = session.query(IntentionToSubmitRequirement).filter(
                IntentionToSubmitRequirement.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=IntentionToSubmitRequirementListNode(items=intention_to_submit_requirement_list,
                                                                      total_count=count),
                            message=f"Successfully to {action_name} Intention To Submit RequirementN")

    # Delete Function
    @staticmethod
    def remove_intention_to_submit_requirement(uid: str):
        """
        Remove Intention To Submit Requirement by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(IntentionToSubmitRequirement).filter_by(uid=uid).update(
                {IntentionToSubmitRequirement.deleted_at: pendulum.now()})
            session.commit()


IntentionToSubmitRequirementCrud = IntentionToSubmitRequirementService(IntentionToSubmitRequirement)
