import math


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
        'A': '70 - < 100',
        'B+': '60 - < 70',
        'B': '50 - < 60',
        'C': '40 - < 50',
        'D': '30 - < 40',
        'E': '0 - < 30',
    }
    letter_grade = ['A', 'B+', 'B', 'C', 'D', 'E']

    def get_course_performance_grade(self, score, program_type):
        if program_type == 'MA' or program_type == 'PGD' or program_type == 'PHD':
            if score >= 75:
                grade_point = 0.024 * score + 2.6
                return {'grade': 'A', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),'description':'Excellent'}
            if score >= 65:
                grade_point = 0.08 * score - 1.6
                return {'grade': 'B+', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),'description':'Very Good'}
            if score >= 60:
                grade_point = 0.1 * score - 3
                return {'grade': 'B', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),'description':'Good'}
            if score >= 50:
                grade_point = 0.1 * score - 3

                return {'grade': 'C', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),'description':'Satisfactory'}
            if score >= 40:
                grade_point = 0.1 * score - 3

                return {'grade': 'D', 'status': 'Fail', 'grade_point': by_law_custom_round(grade_point), 'description':'Marginal Fail'}
            if score >= 0:
                grade_point = 0.025 * score

                return {'grade': 'E', 'status': 'Fail', 'grade_point': by_law_custom_round(grade_point), 'description':'Absolute Fail'}
        else:
            if score >= 70:
                grade_point = 0.02 * score + 3
                return {'grade': 'A', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),'description':'Pass'}
            if score >= 65:
                grade_point = 0.08 * score - 1.2
                return {'grade': 'B+', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),'description':'Pass'}
            if score >= 60:
                grade_point = 0.2 * score - 9
                return {'grade': 'B', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),'description':'Pass'}
            if score >= 50:
                grade_point = 0.1 * score - 3

                return {'grade': 'C', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point),'description':'Pass'}
            if score >= 40:
                grade_point = 0.1 * score - 3

                return {'grade': 'D', 'status': 'Fail', 'grade_point': by_law_custom_round(grade_point),'description':'Pass'}
            if score >= 0:
                grade_point = 0.025 * score

                return {'grade': 'E', 'status': 'Fail', 'grade_point': by_law_custom_round(grade_point),'description':'Pass'}




def by_law_custom_round(value):
    return math.floor(value * 100) / 100
