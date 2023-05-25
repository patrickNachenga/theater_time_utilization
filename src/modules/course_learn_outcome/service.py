from typing import List

import pendulum
from sqlalchemy import select
from src.db.session import session_scope
from src.models.course_learn_outcome import CourseLearnOutcome
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseLearnOutcomeInput, CourseLearnOutcomeNode


class CourseLearnOutcomeService(object):
    @staticmethod
    def get_course_learn_outcome() -> List[CourseLearnOutcome]:
        with session_scope() as session:
            result = session.query(
                CourseLearnOutcome.id,
                CourseLearnOutcome.uid,
                CourseLearnOutcome.staff_id,
                CourseLearnOutcome.program_course_id,
                CourseLearnOutcome.learning_outcome,
                CourseLearnOutcome.created_by,
                CourseLearnOutcome.created_at,
                CourseLearnOutcome.updated_at,
            ).filter(CourseLearnOutcome.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_course_learn_outcome_by_ids(ids: List[str]) -> List[CourseLearnOutcome]:
        """
        Get course learn outcome by ids
        :return:
        """
        with session_scope() as session:
            stmt = select(CourseLearnOutcome).where(
                (CourseLearnOutcome.id.in_(ids)) & (CourseLearnOutcome.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_course_learn_outcome_by_uids(uids: List[str]) -> List[CourseLearnOutcome]:
        """
        Get course learn outcome by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(CourseLearnOutcome).where(
                (CourseLearnOutcome.uid.in_(uids)) & (CourseLearnOutcome.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_course_learn_outcome_by_uid(uid: str) -> List[CourseLearnOutcome]:
        """
        Get one course learn outcome by id
        :return:
        """
        with session_scope() as session:
            stmt = select(CourseLearnOutcome).where(
                (CourseLearnOutcome.uid.in_(uid)) & (CourseLearnOutcome.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    def register_course_learn_outcome(self, inputs: List[CourseLearnOutcomeInput]) -> Response[List[CourseLearnOutcomeNode]]:
        """
        Register Course Learn outcome semesters
        :param inputs:
        :return:
        """
        course_learn_outcome_list = []
        action_type = "Register"
        print("---------------------------------------------------------------")
        with session_scope() as session:
            # Check if the course learn outcome already exist using uid
            existed_course_learn_outcome_list = self.get_course_learn_outcome_by_uids(
                [course_learn_outcome.program_course_id for course_learn_outcome in inputs if course_learn_outcome.uid is None])
            if existed_course_learn_outcome_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_course_learn_outcome_list,
                                message="Course Learn outcome Already Exists")
            # check for existing course learn outcome using uid
            existed_course_learn_outcome = self.get_course_learn_outcome_by_uids(
                [inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    course_learn_outcome = CourseLearnOutcome(
                        staff_id=inputItem.staff_id,
                        program_course_id=inputItem.program_course_id,
                        learning_outcome=inputItem.learning_outcome
                    )
                    course_learn_outcome_list.append(course_learn_outcome)
                else:
                    action_type = "Update"
                    course_learn_outcome = next(
                        filter(lambda course_learn_outcome: str(course_learn_outcome.uid) == str(inputItem.uid),
                               existed_course_learn_outcome), None)

                    if course_learn_outcome:
                        course_learn_outcome.staff_id = inputItem.staff_id
                        course_learn_outcome.program_course_id = inputItem.program_course_id
                        course_learn_outcome.learning_outcome = inputItem.learning_outcome
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
