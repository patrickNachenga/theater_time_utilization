from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc
from src.db.session import session_scope
from src.models.course_learn_outcome import CourseLearnOutcome
from src.modules import CRUDBase
from src.modules.program_course.service import ProgramCourseService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseLearnOutcomeInput, CourseLearnOutcomeListNode


class CourseLearnOutcomeService(CRUDBase[CourseLearnOutcome, CourseLearnOutcomeInput, CourseLearnOutcomeInput]):
    @staticmethod
    def get_course_learn_outcome() -> List[CourseLearnOutcome]:
        with session_scope() as session:
            result = session.query(CourseLearnOutcome).filter(CourseLearnOutcome.deleted_at.is_(None)).order_by(
                desc(CourseLearnOutcome.updated_at)).all()
            return result

    @staticmethod
    def get_course_learn_outcome_by_uids(uids: List[str]) -> List[CourseLearnOutcome]:
        """
        Get course learn outcome by uids
        :return uids:
        """
        with session_scope() as session:
            stmt = select(CourseLearnOutcome).where(
                (CourseLearnOutcome.uid.in_(uids)) & (CourseLearnOutcome.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_course_learn_outcome_by_uid(uid: str) -> CourseLearnOutcome:
        """
        Get one course learn outcome by id
        :return:
        """
        with session_scope() as session:
            stmt = select(CourseLearnOutcome).where((CourseLearnOutcome.uid == uid) & (CourseLearnOutcome.deleted_at.is_(None))).order_by(
                desc(CourseLearnOutcome.updated_at))
            result = session.scalars(stmt)
            return result.all()

    def register_course_learn_outcome(self, inputs: List[CourseLearnOutcomeInput]) -> Response[CourseLearnOutcomeListNode]:
        """
        Register Course Learn outcome
        :param inputs:
        :return:
        """
        course_learn_outcome_list = []
        action_type = "Register"
        with session_scope() as session:
            # check for existing course learn outcome using uid
            existed_course_learn_outcome = self.get_course_learn_outcome_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                # Verify and get supplied Course learn outcome uid. and get existed Course learn outcome id from returned model
                try:
                    program_course_id = ProgramCourseService.get_program_course_by_uid(inputItem.program_course_uid).id
                except Exception as e:
                    print(e)
                    return Response(status=False, code=ResponseCode.FAILURE,
                                    data=CourseLearnOutcomeListNode(items=[], total_count=0),
                                    message="You have submitted incorrect program course details")

                if inputItem.uid is None:
                    course_learn_outcome = CourseLearnOutcome(
                        staff_uid=inputItem.staff_uid,
                        program_course_id=program_course_id,
                        learning_outcome=inputItem.learning_outcome
                    )
                    course_learn_outcome_list.append(course_learn_outcome)
                else:
                    action_type = "Update"
                    course_learn_outcome = next(
                        filter(lambda learn_outcome: str(learn_outcome.uid) == str(inputItem.uid),
                               existed_course_learn_outcome), None)

                    if course_learn_outcome:
                        obj_data = jsonable_encoder(inputItem)
                        # Replace referenced uids field with model required ids field
                        obj_data['program_course_id'] = program_course_id
                        for key, value in obj_data.items():
                            setattr(course_learn_outcome, key, value)

                        course_learn_outcome_list.append(course_learn_outcome)
            session.add_all(course_learn_outcome_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=course_learn_outcome_list,
                            message=f"Successfully to {action_type} Course Learn Outcome")

    # Delete FUnction
    @staticmethod
    def remove_course_learn_outcome(uid: str):
        """
        Remove Course Learn Outcome by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(CourseLearnOutcome).filter_by(uid=uid).update({CourseLearnOutcome.deleted_at: pendulum.now()})
            session.commit()


CourseLearnOutcomeCrud = CourseLearnOutcomeService(CourseLearnOutcome)
