from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc

from src.db.session import session_scope
from src.models import ProgramCourse
from src.models.course_allocation import CourseAllocation
from src.modules import CRUDBase
from src.modules.program_course.service import ProgramCourseService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseAllocationInput, CourseAllocationNode, CourseAllocationListNode


class CourseAllocationService(CRUDBase[CourseAllocation, CourseAllocationInput, CourseAllocationInput]):
    @staticmethod
    def get_course_allocations() -> List[CourseAllocation]:
        with session_scope() as session:
            result = session.query(CourseAllocation).filter(CourseAllocation.deleted_at.is_(None)).order_by(
                desc(CourseAllocation.updated_at)).all()
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
            stmt = select(CourseAllocation).where((CourseAllocation.uid == uid) & (CourseAllocation.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_course_allocations(self, inputs: List[CourseAllocationInput]) -> Response[CourseAllocationListNode]:
        """
        Register Course Allocations
        :param inputs:
        :return:
        """
        course_allocation_list = []
        action_type = "Register"
        with session_scope() as session:
            # check for existing course allocation using uid
            existed_course_allocation = self.get_course_allocations_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                program_course = ProgramCourseService(ProgramCourse).get_program_course_by_uid(inputItem.program_course_uid)
                if program_course is None:
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=CourseAllocationListNode(items=[], total_count=0),
                        message="You have submitted incorrect program course values"
                    )

                if inputItem.uid is None:
                    course_allocation = CourseAllocation(
                        program_course=program_course,
                        staff_uid=inputItem.staff_uid,
                    )
                    local_object = session.merge(course_allocation)
                    session.add(local_object)
                    session.commit()
                    course_allocation_list.append(local_object)
                else:
                    action_type = "Update"
                    course_allocation = next(
                        filter(lambda course_alloc: str(course_alloc.uid) == str(inputItem.uid),
                               existed_course_allocation), None)
                    if course_allocation:
                        obj_data = jsonable_encoder(inputItem)
                        # # Replace referenced uids field with model required ids field
                        obj_data['program_course'] = program_course
                        for key, value in obj_data.items():
                            setattr(program_course, key, value)

                        local_object = session.merge(course_allocation)
                        session.add(local_object)
                        session.commit()
                        course_allocation_list.append(local_object)

            count = session.query(CourseAllocation).filter(CourseAllocation.deleted_at.is_(None)).count()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=CourseAllocationListNode(items=course_allocation_list, total_count=count),
                            message=f"Successfully to {action_type} Course Allocation")

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
