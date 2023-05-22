import strawberry

from src.modules.course.apis import CourseQuery, CourseMutation
from src.modules.groups.apis import GroupQuery, GroupMutation
from src.modules.program_type.apis import ProgramCategoryQuery, ProgramCategoryMutation
from src.modules.programs.apis import ProgramQuery, ProgramMutation
from src.modules.staff.apis import StaffQuery, StaffMutation
from src.modules.students.apis import StudentQuery, StudentMutation
from src.modules.exam_results.apis import ExamResultsQuery, ExamResultsMutation
from src.modules.exam_summary.apis import ExamSummaryQuery, ExamSummaryMutation
from src.modules.exam_cats.apis import ExamCatsQuery, ExamCatsMutation
from src.modules.exam_cat_groups.apis import ExamCatGroupsQuery, ExamCatGroupsMutation

@strawberry.type
class ApiQuery(StudentQuery, StaffQuery, ProgramCategoryQuery, CourseQuery, GroupQuery, ProgramQuery,
               ExamCatGroupsQuery,ExamCatsQuery,ExamResultsQuery,
               ExamSummaryQuery):
    pass


@strawberry.type
class ApiMutation(StudentMutation, StaffMutation, ProgramCategoryMutation, CourseMutation, GroupMutation,
                  ProgramMutation, ExamCatGroupsMutation, ExamCatsMutation,
                  ExamResultsMutation, ExamSummaryMutation):
    pass
