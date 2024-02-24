from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import aliased

from src.db.session import session_scope
from src.models import AcademicYear, ExamCategory, ProgramCourse, ProgramSemester, Course,ExamResultSummary
from src.models.exam_coursework import ExamCoursework
from src.shared.response_code import ResponseCode
from src.types import StudentCourseWorkOutput, ExamCourseWorkNode, Score, CourseWorkTypeOutput, ExamCourseWorkSearchCriteria
from src.shared.response import Response


class ExamCourseworkService:

    @staticmethod
    def get_exam_course_work_results(search_criteria: ExamCourseWorkSearchCriteria) -> List[ExamCourseWorkNode]:
        with (session_scope() as session):

            # query = session.query(ExamCoursework).filter(ExamCoursework.deleted_at.is_(None))
            exam_category_alias = aliased(ExamCategory)

            # Subquery to select the latest entry for each student_uid
            latest_exam_result_summary_subquery = (
                session.query(
                    ExamResultSummary.student_uid,
                    func.row_number().over(
                        partition_by=ExamResultSummary.student_uid,
                        order_by=ExamResultSummary.created_at.desc()
                        # Assuming there's a date column indicating the latest entry
                    ).label('row_number')
                )
                .subquery()
            )

            # Modify the original query to filter based on the subquery
            query = (
                session.query(
                    ExamCoursework,
                    exam_category_alias.code.label('exam_category_code'),
                    exam_category_alias.name.label('exam_category_name'),
                    ExamResultSummary.first_name,
                    ExamResultSummary.middle_name,
                    ExamResultSummary.last_name,
                    ExamResultSummary.registration_number,
                )
                .join(ExamCategory, ExamCoursework.exam_category_id == ExamCategory.id)
                .join(
                    ExamResultSummary,
                    ExamCoursework.student_uid == ExamResultSummary.student_uid
                )
                .join(
                    latest_exam_result_summary_subquery,
                    latest_exam_result_summary_subquery.c.student_uid == ExamResultSummary.student_uid
                )
                .filter(
                    ExamCoursework.deleted_at.is_(None),
                    latest_exam_result_summary_subquery.c.row_number == 1  # Select only the latest entry
                )
            )

            if search_criteria.student_uid:
                query = query.filter(ExamCoursework.student_uid == search_criteria.student_uid)

            if search_criteria.program_course_id:
                query = query.filter(ExamCoursework.program_course_id == search_criteria.program_course_id)

            if search_criteria.exam_category_id:
                query = query.filter(ExamCoursework.exam_category_id == search_criteria.exam_category_id)

            query = query.order_by(ExamCoursework.student_uid.asc(), ExamCoursework.exam_category_id.asc(), ExamCoursework.assessment_number.asc())

            results = query.all()
            print("results:", results)
            return results

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
                    Course.name.label("course_name"),
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
                .group_by(ProgramCourse.id, Course.code, Course.name)
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
                    # print(course_type)
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
                            "course_name": course.course_name,
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
                                                                                   course_name=item['course_name'],
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
                message="Course work has not been uploaded yet.",
                data=[]
            )

exam_coursework_service = ExamCourseworkService()
