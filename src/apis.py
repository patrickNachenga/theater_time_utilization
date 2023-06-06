import strawberry

from src.modules.course.apis import CourseQuery, CourseMutation
from src.modules.course_allocation.apis import CourseAllocationQuery, CourseAllocationMutation
from src.modules.course_category.apis import CourseCategoryQuery, CourseCategoryMutation
from src.modules.course_learn_outcome.apis import CourseLearnOutcomeQuery, CourseLearnOutcomeMutation
from src.modules.groups.apis import GroupQuery, GroupMutation
from src.modules.program_category.apis import ProgramCategoryQuery, ProgramCategoryMutation
from src.modules.program_course.apis import ProgramCourseQuery, ProgramCourseMutation
from src.modules.program_semester.apis import ProgramSemesterQuery, ProgramSemesterMutation
from src.modules.programs.apis import ProgramQuery, ProgramMutation
from src.modules.sr2_api_calls.apis import Sr2Query
from src.modules.staff.apis import StaffQuery, StaffMutation
from src.modules.students.apis import StudentQuery, StudentMutation
from src.modules.exam_results.apis import ExamResultsQuery, ExamResultsMutation
from src.modules.exam_summary.apis import ExamSummaryQuery, ExamSummaryMutation
from src.modules.exam_cats.apis import ExamCatsQuery, ExamCatsMutation
from src.modules.exam_cat_groups.apis import ExamCatGroupsQuery, ExamCatGroupsMutation
from src.modules.academic_year.apis import AcademicYearQuery, AcademicYearMutation
from src.modules.program_course_assessment.apis import ProgramCourseAssessmentQuery, ProgramCourseAssessmentMutation


@strawberry.type
class ApiQuery(StudentQuery, StaffQuery, ProgramCategoryQuery, CourseQuery, CourseAllocationQuery,
               CourseCategoryQuery, GroupQuery, ProgramQuery, ExamCatGroupsQuery, ExamCatsQuery, ExamResultsQuery,
               ExamSummaryQuery, AcademicYearQuery, ProgramSemesterQuery, CourseLearnOutcomeQuery, ProgramCourseQuery,
               ProgramCourseAssessmentQuery, Sr2Query):
    pass


@strawberry.type
class ApiMutation(StudentMutation, StaffMutation, ProgramCategoryMutation, CourseMutation, CourseAllocationMutation,
                  CourseCategoryMutation, GroupMutation,
                  ExamCatGroupsMutation, ExamCatsMutation,
                  ExamResultsMutation, ExamSummaryMutation, AcademicYearMutation,
                  ProgramSemesterMutation, CourseLearnOutcomeMutation, ProgramCourseMutation, ProgramMutation,
                  ProgramCourseAssessmentMutation):
    pass
