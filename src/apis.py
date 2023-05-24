import strawberry

from src.modules.course.apis import CourseQuery, CourseMutation
from src.modules.course_learn_outcome.apis import CourseLearnOutcomeQuery, CourseLearnOutcomeMutation
from src.modules.groups.apis import GroupQuery, GroupMutation
from src.modules.program_category.apis import ProgramCategoryQuery, ProgramCategoryMutation
from src.modules.program_semester.apis import ProgramSemesterQuery, ProgramSemesterMutation
from src.modules.programs.apis import ProgramQuery, ProgramMutation

from src.modules.staff.apis import StaffQuery, StaffMutation
from src.modules.students.apis import StudentQuery, StudentMutation
from src.modules.exam_results.apis import ExamResultsQuery, ExamResultsMutation
from src.modules.exam_summary.apis import ExamSummaryQuery, ExamSummaryMutation
from src.modules.exam_cats.apis import ExamCatsQuery, ExamCatsMutation
from src.modules.exam_cat_groups.apis import ExamCatGroupsQuery, ExamCatGroupsMutation
from src.modules.academic_year.apis import AcademicYearQuery, AcademicYearMutation
from src.modules.course_assessment.apis import CourseAssessmentQuery, CourseAssessmentMutation


@strawberry.type
class ApiQuery(StudentQuery, StaffQuery, ProgramCategoryQuery, CourseQuery, GroupQuery, ProgramQuery,
               ExamCatGroupsQuery, ExamCatsQuery, ExamResultsQuery,
               ExamSummaryQuery, AcademicYearQuery, CourseAssessmentQuery, ProgramSemesterQuery, CourseLearnOutcomeQuery):
    pass


@strawberry.type
class ApiMutation(StudentMutation, StaffMutation, ProgramCategoryMutation, CourseMutation, GroupMutation,
                  ProgramMutation, ExamCatGroupsMutation, ExamCatsMutation, ExamResultsMutation, ExamSummaryMutation,
                  AcademicYearMutation, CourseAssessmentMutation, ProgramSemesterMutation, CourseLearnOutcomeMutation):
    pass
