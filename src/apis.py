import strawberry

from src.modules.program_type.apis import ProgramCategoryQuery, ProgramCategoryMutation
from src.modules.staff.apis import StaffQuery, StaffMutation
from src.modules.students.apis import StudentQuery, StudentMutation

@strawberry.type
class ApiQuery(StudentQuery, StaffQuery, ProgramCategoryQuery):
    pass


@strawberry.type
class ApiMutation(StudentMutation, StaffMutation, ProgramCategoryMutation):
    pass