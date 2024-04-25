import math

from sqlalchemy import func, case

from src.models import ProgramCourseAssessment, ProgramCourse, ExamCategory


class ByLaw2019:
    grade_classification_undergraduate = {
        'A': '70 - < 100',
        'B+': '65 - < 69.9',
        'B': '60 - < 64.9',
        'C': '50 - < 59.9',
        'D': '40 - < 49.9',
        'E': '0 - < 39.9',
    }

    grade_classification_postgraduate = {
        'A': '75 - < 100',
        'B+': '65 - < 75',
        'B': '60 - < 65',
        'C': '50 - < 60',
        'D': '40 - < 50',
        'E': '0 - < 40',
    }
    letter_grade = ['A', 'B+', 'B', 'C', 'D', 'E']

    def get_course_performance_grade(self, result_summary, program_type, session):
        score = result_summary.total_score
        # check if program course assessment has exam category of ue practical
        c_type = self.get_contribution_type(result_summary,session)
        if program_type == 'MA' or program_type == 'PGD' or program_type == 'PHD':
            if score >= 75:
                grade_point = 0.024 * score + 2.6
                return {'grade': 'A', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),
                        'description': 'Excellent'}
            if score >= 65:
                grade_point = 0.08 * score - 1.6
                return {'grade': 'B+', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),
                        'description': 'Very Good'}
            if score >= 60:
                grade_point = 0.1 * score - 3
                return {'grade': 'B', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),
                        'description': 'Good'}
            if score >= 50:
                grade_point = 0.1 * score - 3

                return {'grade': 'C', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),
                        'description': 'Satisfactory'}
            if score >= 40:
                grade_point = 0.1 * score - 3

                return {'grade': 'D', 'status': 'Fail', 'grade_point': by_law_custom_round(grade_point),
                        'description': 'Marginal Fail'}
            if score >= 0:
                grade_point = 0.025 * score

                return {'grade': 'E', 'status': 'Fail', 'grade_point': by_law_custom_round(grade_point),
                        'description': 'Absolute Fail'}
        else:
            if score >= 70:
                grade_point = 0.02 * score + 3
                return {'grade': 'A'+c_type, 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),
                        'description': 'Pass'}
            if score >= 65:
                grade_point = 0.08 * score - 1.2
                return {'grade': 'B+'+c_type, 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),
                        'description': 'Pass'}
            if score >= 60:
                grade_point = 0.2 * score - 9
                return {'grade': 'B'+c_type, 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),
                        'description': 'Pass'}
            if score >= 50:
                grade_point = 0.1 * score - 3

                return {'grade': 'C'+c_type, 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),
                        'description': 'Pass'}
            if score >= 40:
                grade_point = 0.1 * score - 3

                return {'grade': 'D'+c_type, 'status': 'Fail', 'grade_point': by_law_custom_round(grade_point),
                        'description': 'Pass'}
            if score >= 0:
                grade_point = 0.025 * score

                return {'grade': 'E'+c_type, 'status': 'Fail', 'grade_point': by_law_custom_round(grade_point),
                        'description': 'Pass'}

    def get_contribution_type(self, result_summary, session):
        # Define a case statement to sum maximum_score based on is_theory
        assessment_with_ue_practical = session.query(
            ProgramCourseAssessment
        ).join(ProgramCourse).filter(ProgramCourseAssessment.program_course.has(id=result_summary.program_course_id),
                                     ProgramCourse.id == result_summary.program_course_id,
                                     ProgramCourseAssessment.exam_category.has(is_ue=True),
                                     ProgramCourseAssessment.exam_category.has(is_theory=False)).all()
        if assessment_with_ue_practical:

            sum_max_score_practical = func.sum(
                case([(ExamCategory.is_theory == False, ProgramCourseAssessment.maximum_score)], else_=0)
            ).label('sum_maximum_score_practical')

            sum_max_score_theory = func.sum(
                case([(ExamCategory.is_theory == True, ProgramCourseAssessment.maximum_score)], else_=0)
            ).label('sum_maximum_score_theory')

            # Query to calculate the sums
            query = (
                session.query(sum_max_score_practical, sum_max_score_theory)
                .join(ExamCategory)
                .filter(ProgramCourseAssessment.program_course_id == result_summary.program_course_id)
                .group_by(ProgramCourseAssessment.program_course_id)
            )

            result = query.first()

            # Result will contain the sums
            sum_maximum_score_practical = result.sum_maximum_score_practical  # practical
            sum_maximum_score_theory = result.sum_maximum_score_theory  # theory
            t = ''
            p = ''
            if (result_summary.cw_practical + result_summary.ue_practical) < sum_maximum_score_practical / 2:
                p = '|P'
            if (result_summary.cw_theory + result_summary.ue_theory) < sum_maximum_score_theory / 2:
                t = '|T'
            return p + t
        else:
            return ''


def by_law_custom_round(value):
    return math.floor(value * 100) / 100
