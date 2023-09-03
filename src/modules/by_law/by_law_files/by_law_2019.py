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

    def get_course_performance_grade(self, score):
        if score >= 70:
            grade_point = 0.02 * score + 3
            return {'grade': 'A', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point)}
        if score >= 65:
            grade_point = 0.08 * score - 1.2
            return {'grade': 'B+', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point)}
        if score >= 60:
            grade_point = 0.02 * score - 9
            return {'grade': 'B', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point)}
        if score >= 50:
            grade_point = 0.1 * score - 3

            return {'grade': 'C', 'status': 'Pass', 'grade_point': by_law_custom_round(grade_point)}
        if score >= 40:
            grade_point = 0.1 * score - 3

            return {'grade': 'D', 'status': 'Fail', 'grade_point': by_law_custom_round(grade_point)}
        if score >= 0:
            grade_point = 0.025 * score

            return {'grade': 'E', 'status': 'Fail', 'grade_point': by_law_custom_round(grade_point)}

    def get_grade_point(self, latter_grade):
        if latter_grade == 'A':
            return 5
        if latter_grade == 'B+':
            return 4
        if latter_grade == 'B':
            return 3
        if latter_grade == 'C':
            return 2
        if latter_grade == 'D':
            return 1
        if latter_grade == 'E':
            return 0


def by_law_custom_round(value):
    return math.floor(value * 100) / 100
