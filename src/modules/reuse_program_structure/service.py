from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc
from src.db.session import session_scope
from src.models import Program, AcademicYear
from src.models.program_semester import ProgramSemester
from src.models import ProgramCourse
from src.modules import CRUDBase
from src.modules.academic_year.service import AcademicYearService
from src.modules.programs.service import ProgramService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramSemesterInput, ReuseProgramStructureInput, ProgramSemesterListNode


class ProgramStructureService(CRUDBase[ProgramSemester, ProgramSemesterInput, ProgramSemesterInput]):
    @staticmethod
    def get_program_semesters() -> List[ProgramSemester]:
        with session_scope() as session:
            result = session.query(ProgramSemester).filter(ProgramSemester.deleted_at.is_(None)).order_by(
                desc(ProgramSemester.updated_at)).all()
            return result

    @staticmethod
    def get_program_semesters_by_ids(ids: List[str]) -> List[ProgramSemester]:
        """
        Get programs semesters by ids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where(
                (ProgramSemester.id.in_(ids)) & (ProgramSemester.deleted_at.is_(None))).order_by(
                desc(ProgramSemester.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_semester_by_uid(uid: str) -> ProgramSemester:
        """
        Get program semester by uid
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where(
                (ProgramSemester.uid == uid) & (ProgramSemester.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_academic_year_name_by_uid(uid: str, name: str) -> str:
        """
        Get a specific attribute of an Academic Year by uid
        :param uid: The uid of the Academic Year
        :param attribute: The attribute to retrieve
        :return: The value of the specified attribute or None if not found
        """
        with session_scope() as session:
            stmt = select(getattr(AcademicYear, name)).where(
                (AcademicYear.uid == uid) & (AcademicYear.deleted_at.is_(None))
            )
            result = session.execute(stmt).scalar()
            return result

    @staticmethod
    def get_academic_year_uid_by_name(name: str, uid: str) -> str:
        """
        Get a specific attribute of an Academic Year by uid
        :param uid: The uid of the Academic Year
        :param attribute: The attribute to retrieve
        :return: The value of the specified attribute or None if not found
        """
        with session_scope() as session:
            stmt = select(getattr(AcademicYear, uid)).where(
                (AcademicYear.name == name) & (AcademicYear.deleted_at.is_(None))
            )
            result = session.execute(stmt).scalar()
            return result

    @staticmethod
    def check_program_courses(program_semester_id: int) -> List[ProgramCourse]:
        """
        Check if there already exists program course with same course_id, program_semester_id all together
        :return ProgramCourse:
        """
        with session_scope() as session:
            stmt = select(ProgramCourse).where(
                (ProgramCourse.program_semester_id == program_semester_id) &
                (ProgramCourse.deleted_at.is_(None))
            )
            result = session.scalars(stmt)
            return result.all()
    @staticmethod
    def get_academic_year_id_by_name(name: str, id: str) -> int:
        """
        Get a specific attribute of an Academic Year by uid
        :param uid: The uid of the Academic Year
        :param attribute: The attribute to retrieve
        :return: The value of the specified attribute or None if not found
        """
        with session_scope() as session:
            stmt = select(getattr(AcademicYear, id)).where(
                (AcademicYear.name == name) & (AcademicYear.deleted_at.is_(None))
            )
            result = session.execute(stmt).scalar()
            return result

    @staticmethod
    def get_program_semester_by_uids(uids: List[str]) -> List[ProgramSemester]:
        """
        Get programs category by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where(
                (ProgramSemester.uid.in_(uids)) & (ProgramSemester.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def check_uniqueness(academic_year_id: int, program_id: int, study_year: int, semester: int) -> ProgramSemester:
        """
        Check if there already exists program semester with same academicYearId, programId, studyYear, semester all together
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where(
                (ProgramSemester.academic_year_id == academic_year_id) &
                (ProgramSemester.program_id == program_id) &
                (ProgramSemester.study_year == study_year) &
                (ProgramSemester.semester == semester) &
                (ProgramSemester.deleted_at.is_(None))
            )
            result = session.scalars(stmt)
            return result.first()

    def reuse_program_structure(self, inputs: List[ReuseProgramStructureInput]) -> Response[ProgramSemesterListNode]:
        """
        Register programs semesters
        :param inputs:
        :return:
        """
        program_semester_list = []
        action_type = "Register"

        with session_scope() as session:
            # check for existing programs semesters using uid
            # existed_program_semester = self.get_program_semester_by_uids([inputItem.uid for inputItem in inputs])

            for inputItem in inputs:
                # Verify and get supplied Program uid and get existed program model
                try:
                    program = ProgramService(Program).get(inputItem.program_uid)
                    if program is None:
                        raise ValueError("You have submitted incorrect program details")
                except Exception as e:
                    print(e)
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=ProgramSemesterListNode(items=[], total_count=0),
                        message=f"You have submitted incorrect program details {inputItem.program_uid}"
                    )

                # Verify and get supplied Academic year uid and get existed Academic year model
                try:
                    academic_year = AcademicYearService(AcademicYear).get(inputItem.academic_year_uid)
                    if academic_year is None:
                        raise ValueError("You submitted incorrect academic year details")
                except Exception as e:
                    print(e)
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=ProgramSemesterListNode(items=[], total_count=0),
                        message="You submitted incorrect academic year details"
                    )

                deprecated_program_semester = self.check_uniqueness(academic_year_id=academic_year.id,
                                                                    program_id=program.id,
                                                                    semester=inputItem.semester,
                                                                    study_year=inputItem.study_year
                                                                    )
                if deprecated_program_semester:
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=ProgramSemesterListNode(items=[], total_count=0),
                        message=f"Program Semester Already Exist {deprecated_program_semester.id}"
                    )

                academic_year_name = inputItem.academic_year_uid
                academic_year = AcademicYearService(AcademicYear).get(inputItem.academic_year_uid)
                # manager = AcademicYearManager()

                # Call the get_academic_year_attribute_by_uid function
                uid = inputItem.academic_year_uid
                attribute = "name"  # Replace with the actual attribute name
                result = self.get_academic_year_name_by_uid(uid, attribute)
                previous_year = result.split('/')
                previous_academic_year_name = str(int(previous_year[0]) - 1) + "/" + str(int(previous_year[1]) - 1)

                attribute = "uid"
                # Get the Previous Academic Year uid by Name
                previous_academic_year_uid = self.get_academic_year_uid_by_name(previous_academic_year_name, attribute)
                attribute = "id"
                previous_academic_year_id = self.get_academic_year_id_by_name(previous_academic_year_name, attribute)

                # Get Previous Program Semester Details
                previous_program_semester = self.check_uniqueness(academic_year_id=previous_academic_year_id,
                                                                  program_id=program.id,
                                                                  semester=inputItem.semester,
                                                                  study_year=inputItem.study_year)

                if previous_program_semester:

                    # Prepare and Record the Desired Program Semester
                    program_semester = ProgramSemester(
                        study_year=inputItem.study_year,
                        semester=inputItem.semester,
                        program=program,
                        academic_year=academic_year,
                        core_credits=previous_program_semester.core_credits,
                        elective_credits=previous_program_semester.elective_credits
                    )
                    local_object = session.merge(program_semester)
                    session.add(local_object)
                    session.commit()
                    program_semester_list.append(local_object)

                    # Get Current Program Semester ID after Saving
                    current_program_semester = self.check_uniqueness(academic_year_id=academic_year.id,
                                                                     program_id=program.id,
                                                                     semester=inputItem.semester,
                                                                     study_year=inputItem.study_year)

                    check_program_courses_list = self.check_program_courses(program_semester_id=previous_program_semester.id
                                                                       )
                    if check_program_courses_list:
                        print('-----Courses Available')
                        #     Prepare and Create Program Courses for current Academic Year
                        for program_courses in check_program_courses_list:
                            program_course = ProgramCourse(
                                program_semester=current_program_semester,
                                course=program_courses.course,
                                credit=program_courses.credit,
                                course_category=program_courses.course_category,
                                lecture_hours=program_courses.lecture_hours,
                                seminar_hours=program_courses.seminar_hours,
                                practical_hours=program_courses.practical_hours,
                                assignment_hours=program_courses.assignment_hours,
                                independent_study_hours=program_courses.independent_study_hours,
                                pass_hours=program_courses.pass_hours
                            )
                            local_object = session.merge(program_course)
                            session.add(local_object)
                            session.commit()
                            program_semester_list.append(local_object)
                        return Response(
                            status=False,
                            code=ResponseCode.SUCCESS,
                            data=ProgramSemesterListNode(items=[], total_count=0),
                            message=f"The Current Program Semester and Program Courses Created Successfully"
                        )

                    else:
                        print('-----Previous Program Courses Settings not Available')

                    return Response(
                        status=False,
                        code=ResponseCode.SUCCESS,
                        data=ProgramSemesterListNode(items=[], total_count=0),
                        message=f"The Current Program Semester Created Successfully"
                    )
                else:

                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=ProgramSemesterListNode(items=[], total_count=0),
                        message=f"The Previous Program Semester Does not Exist"
                    )

            count = session.query(ProgramSemester).filter(ProgramSemester.deleted_at.is_(None)).count()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=ProgramSemesterListNode(items=program_semester_list, total_count=count),
                            message=f"Successfully to  Program Semester")


ProgramSemesterCrud = ProgramStructureService(ProgramSemester)
