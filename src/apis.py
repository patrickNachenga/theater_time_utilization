import strawberry

from src.modules.staff.apis import StaffQuery, StaffMutation
from src.modules.students.apis import StudentQuery, StudentMutation

@strawberry.type
class ApiQuery(StudentQuery, StaffQuery):
    pass


@strawberry.type
class ApiMutation(StudentMutation, StaffMutation):
    pass