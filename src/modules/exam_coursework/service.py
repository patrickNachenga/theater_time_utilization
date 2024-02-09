from typing import List

from sqlalchemy import and_

from src.db.session import session_scope
from src.models import AcademicYear, ExamCategory, ProgramCourse, ProgramSemester, Course
from src.models.exam_coursework import ExamCoursework
from src.shared.response_code import ResponseCode
from src.types import StudentCourseWorkOutput, Score, CourseWorkTypeOutput
from src.shared.response import Response


class ExamCourseworkService:

    @staticmethod
    def get_exam_course_work_results() -> List[ExamCoursework]:
        with session_scope() as session:
            result = session.query(ExamCoursework).filter(ExamCoursework.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_student_exam_course_work_results(student_uid) -> List[ExamCoursework]:
        with session_scope() as session:
            result = session.query(ExamCoursework).filter(ExamCoursework.student_uid == student_uid,
                                                          ExamCoursework.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_student_active_semester_course_work_results(input) -> List[StudentCourseWorkOutput]:
        with session_scope() as session:
            academic_year = session.query(AcademicYear.id).filter(AcademicYear.uid == input.academic_year_uid).first()
            if academic_year is None:
                return Response(
                    status=False,
                    code=ResponseCode.NO_RECORD_FOUND,
                    message="Academic year not found",
                    data=[]
                )
            # print(current_academic_year)
            result = (
                session.query(
                    ProgramCourse.id.label("program_course_id"),
                    Course.code.label("course_code"),
                )
                .join(Course, ProgramCourse.course_id == Course.id)
                .join(ExamCoursework, ExamCoursework.program_course_id == ProgramCourse.id)
                .join(ExamCategory, ExamCoursework.exam_category_id == ExamCategory.id)
                .join(ProgramSemester, ProgramSemester.id == ProgramCourse.program_semester_id)
                .filter(ExamCoursework.student_uid == input.student_uid,
                        ProgramCourse.deleted_at.is_(None),
                        ExamCategory.is_ue.is_(False),
                        ProgramSemester.semester == input.semester,
                        ProgramSemester.study_year == input.study_year,
                        ProgramSemester.academic_year_id == academic_year.id)
                .group_by(ProgramCourse.id, Course.code)
                .all()
            )

            course_data = []
            if result:
                for course in result:
                    course_type = session.query(ExamCategory.name, ExamCategory.id). \
                        join(ExamCoursework, ExamCategory.id == ExamCoursework.exam_category_id). \
                        filter(
                        and_(
                            ExamCoursework.program_course_id == course.program_course_id,
                            ExamCoursework.student_uid == input.student_uid,
                            ExamCategory.is_ue.is_(False),
                        )
                    ).group_by(ExamCategory.name, ExamCategory.id).all()

                course_type_data = []
                if course_type:
                    for cType in course_type:
                        scores = session.query(ExamCoursework.score, ExamCoursework.overall_marks, ExamCoursework.assessment_number). \
                            filter(ExamCoursework.student_uid == input.student_uid,
                                   ExamCoursework.exam_category_id == cType.id,
                                   ExamCoursework.program_course_id == course.program_course_id). \
                            order_by(ExamCoursework.assessment_number.asc()).all()
                        if scores:
                            scoreData = []
                            for mark in scores:
                                s = {
                                    "score": mark.score,
                                    "overall_marks": mark.overall_marks,
                                    "assessment_number": mark.assessment_number
                                }
                                scoreData.append(s)
                            cInfo = {
                                "type": cType.name,
                                "score": scoreData
                            }
                            course_type_data.append(cInfo)

                    c = {
                        "course_code": course.course_code,
                        "course_work_type": course_type_data
                    }
                    course_data.append(c)

                student_course_work_output_list = []
                for item in course_data:
                    course_work_type_list = []
                    for work_type in item['course_work_type']:
                        score_list = [Score(**score) for score in work_type['score']]
                        course_work_type_list.append(CourseWorkTypeOutput(type=work_type['type'], scores=score_list))
                    student_course_work_output_list.append(StudentCourseWorkOutput(course_code=item['course_code'],
                                                                                   course_work_type=course_work_type_list))
                # print(course_data)
                # return student_course_work_output_list
                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Course Works Results Retrieved Successfully",
                    data=student_course_work_output_list
                )

            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="No Record Found",
                data=[]
            )

exam_coursework_service = ExamCourseworkService()
