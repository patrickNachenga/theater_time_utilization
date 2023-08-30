from optparse import Option
from typing import List, Optional

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc
from sqlalchemy.orm import aliased

from src.db.session import session_scope
from src.models import ProgramCourse, ProgramCourseAssessment, ProgramSemester, AcademicYear
from src.models.course_allocation import CourseAllocation
from src.modules import CRUDBase
from src.modules.academic_year.service import AcademicYearService
from src.modules.program_course.service import ProgramCourseService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseAllocationInput, CourseAllocationListNode, CourseAllocationStaffUpdateInput, \
    CourseAllocationNode, StaffCourseAllocationBySemesterInputs


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
            result = session.query(CourseAllocation).filter(CourseAllocation.uid == uid,
                                                            CourseAllocation.deleted_at.is_(None)).first()
            return result

    @staticmethod
    def get_staff_course_allocation(inputs) -> List[CourseAllocation]:
        """
        Get staff course allocation
        :param inputs:containing staff_uid and program_course_uid
        :return:
        """

        with session_scope() as session:
            if inputs.program_course_uid:
                result = session.query(CourseAllocation) \
                    .join(ProgramCourse).join(ProgramSemester).join(AcademicYear).filter(
                    AcademicYear.status == inputs.is_current) \
                    .filter(
                    CourseAllocation.staff_uid == inputs.staff_uid,
                    CourseAllocation.program_course.has(ProgramCourse.uid == inputs.program_course_uid),
                    CourseAllocation.deleted_at.is_(None))
            else:
                result = session.query(CourseAllocation) \
                    .join(ProgramCourse).join(ProgramSemester).join(AcademicYear).filter(
                    AcademicYear.status == inputs.is_current) \
                    .filter(CourseAllocation.staff_uid == inputs.staff_uid,
                            CourseAllocation.deleted_at.is_(None))

            return result.all()

    @staticmethod
    def get_staff_course_allocation_by_Academic_year_semesters(inputs) -> List[CourseAllocation]:
        """
        Get staff course allocation filter with semester
        :param inputs:containing staff_uid and program_course_uid
        :return:
        """
        with session_scope() as session:
            if inputs:
                if inputs.semester == 1:
                    semesters = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
                else:  # Assuming inputs.semester == 2
                    semesters = [2, 4, 6, 8, 10, 12, 14, 16, 18]

                result = session.query(CourseAllocation).join(ProgramCourse).join(ProgramSemester).join(AcademicYear) \
                    .filter(AcademicYear.status == inputs.is_current) \
                    .filter(CourseAllocation.staff_uid == inputs.staff_uid) \
                    .filter(CourseAllocation.deleted_at.is_(None)) \
                    .filter(ProgramSemester.semester.in_(semesters)) \
                    .filter(CourseAllocation.staff_uid == inputs.staff_uid) \
                    .filter(CourseAllocation.deleted_at.is_(None))
                return result
            else:
                return None

    @staticmethod
    def get_course_allocation_by_program_course_uid(uid: str) -> Response[CourseAllocationListNode]:
        """
        Get Course  Allocation by program semester uid
        :return:
        """
        with session_scope() as session:
            try:
                program_course = ProgramCourseService.get_program_course_by_uid(uid)
                if program_course is None:
                    raise ValueError("You have submitted incorrect programs course details")
            except Exception as e:
                print(e)
                return Response(status=False, code=ResponseCode.FAILURE,
                                data=CourseAllocationListNode(items=[], total_count=0),
                                message="You have submitted incorrect programs course details")

            stmt = select(CourseAllocation).where(
                (CourseAllocation.program_course_id == program_course.id) & (
                    CourseAllocation.deleted_at.is_(None)))
            result_raw = session.scalars(stmt)
            result = result_raw.all()
            count = session.query(CourseAllocation).filter(CourseAllocation.deleted_at.is_(None)).count()
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                data=CourseAllocationListNode(items=result, total_count=count),
                message="Course Allocations Retrieved Successful"
            )

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
                program_course = ProgramCourseService(ProgramCourse).get_program_course_by_uid(
                    inputItem.program_course_uid)
                if program_course is None:
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=CourseAllocationListNode(items=[], total_count=0),
                        message="You have submitted incorrect program course values"
                    )

                if inputItem.uid is None:
                    exist_course_allocation = session.query(CourseAllocation).filter(
                        CourseAllocation.staff_uid == inputItem.staff_uid,
                        CourseAllocation.program_course.has(ProgramCourse.uid == inputItem.program_course_uid),
                        CourseAllocation.deleted_at.is_(None)).all()
                    if exist_course_allocation:
                        return Response(
                            status=False,
                            code=ResponseCode.FAILURE,
                            data=CourseAllocationListNode(items=[], total_count=0),
                            message="Staff has this course already"
                        )
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

    @staticmethod
    def staff_update_allocation_assessment_item(inputs) -> ProgramCourseAssessment:
        """
        this enable Staff to update "can_exceed_minimum_by" to increase number of assessment
        input assessment items uid
        """
        with session_scope() as session:
            session.query(ProgramCourseAssessment).filter_by(uid=inputs.program_course_assessment_uid).update(
                {"can_exceed_minimum_by": inputs.can_exceed_minimum_by}
            )
            session.commit()
            program_course_assessment = session.query(ProgramCourseAssessment).filter(
                ProgramCourseAssessment.uid == inputs.program_course_assessment_uid).first()
            return program_course_assessment

    @staticmethod
    def update_course_allocation_staff(inputs: CourseAllocationStaffUpdateInput) -> CourseAllocationNode:
        # update/change staff in a particular course allocation
        with session_scope() as session:
            session.query(CourseAllocation).filter_by(uid=inputs.uid).update(
                {"staff_uid": inputs.staff_uid}
            )
            session.commit()
            course_allocations = session.query(CourseAllocation).filter(CourseAllocation.uid == inputs.uid,
                                                                        CourseAllocation.deleted_at.is_(None)).first()
            return course_allocations


CourseAllocationCrud = CourseAllocationService(CourseAllocation)
