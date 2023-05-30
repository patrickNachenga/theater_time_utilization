from typing import List

import pendulum
from sqlalchemy import select

from src.db.session import session_scope
from src.models import ProgramCourse
from src.models.course_allocation import CourseAllocation
from src.modules import CRUDBase
from src.modules.program_course.service import ProgramCourseService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseAllocationInput, CourseAllocationNode


class CourseAllocationService(CRUDBase[CourseAllocation, CourseAllocationInput, CourseAllocationInput]):
    @staticmethod
    def get_course_allocations() -> List[CourseAllocation]:
        with session_scope() as session:
            result = session.query(CourseAllocation).filter(CourseAllocation.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_course_allocations_by_uids(uids: List[str]) -> List[CourseAllocation]:
        """
        Get course Allocation by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(CourseAllocation).where(
                (CourseAllocation.uid.in_(uids)) & (CourseAllocation.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_course_by_uid(uid: str) -> CourseAllocation:
        """
        Get course category by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(CourseAllocation).where(
                (CourseAllocation.uid == uid) & (CourseAllocation.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_course_allocations(self, inputs: List[CourseAllocationInput]) -> Response[List[CourseAllocationNode]]:
        """
        Register Course Allocations
        :param inputs:
        :return:
        """
        course_allocation_list = []
        with session_scope() as session:
            # Check if the course allocation already exist using uid
            existed_course_allocation_list = self.get_course_allocations_by_uids(
                [course_allocation.uid for course_allocation in inputs if course_allocation.uid is None])
            if existed_course_allocation_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_course_allocation_list,
                                message="Course Allocation Already Exists")
            # check for existing course category using uid
            existed_course_allocation = self.get_course_allocations_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:

                try:
                    program_course_id = ProgramCourseService(ProgramCourse).get_program_course_by_uid(inputItem.uid).id
                except Exception as e:
                    print(e)
                    return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_course_allocation_list,
                                    message="Please make sure you have submitted correct program course values")


                if inputItem.uid is None:
                    course_allocation = CourseAllocation(
                        program_course_id=program_course_id,
                        staff_uid=inputItem.staff_uid,

                    )
                    course_allocation_list.append(course_allocation)
                else:
                    course_allocation = next(
                        filter(lambda course_allocation: str(course_allocation.uid) == str(inputItem.uid),
                               existed_course_allocation), None)
                    if course_allocation:
                        course_allocation.program_course_id = program_course_id,
                        course_allocation.staff_uid = inputItem.staff_uid,

            session.add_all(course_allocation_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=course_allocation_list,
                            message="Successfully Submitted")

    # Delete Function
    @staticmethod
    def remove_course_allocation(uid: str):
        """
        Remove course allocation by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(CourseAllocation).filter_by(uid=uid).update({CourseAllocation.deleted_at: pendulum.now()})
            session.commit()


CourseAllocationCrud = CourseAllocationService(CourseAllocation)
