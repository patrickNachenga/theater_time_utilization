import strawberry

from src.modules.course.apis import CourseQuery, CourseMutation
from src.modules.groups.apis import GroupQuery, GroupMutation
from src.modules.program_type.apis import ProgramCategoryQuery, ProgramCategoryMutation
from src.modules.program.apis import ProgramQuery, ProgramMutation
from src.modules.staff.apis import StaffQuery, StaffMutation
from src.modules.students.apis import StudentQuery, StudentMutation


@strawberry.type
class ApiQuery(StudentQuery, StaffQuery, ProgramCategoryQuery, CourseQuery, GroupQuery, ProgramQuery):
    pass


@strawberry.type
class ApiMutation(StudentMutation, StaffMutation, ProgramCategoryMutation, CourseMutation, GroupMutation, ProgramMutation):
    pass
