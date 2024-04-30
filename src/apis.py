import strawberry

from src.modules.academic_year.apis import AcademicYearQuery, AcademicYearMutation
from src.modules.academic_year_semester.apis import AcademicYearSemesterQuery, AcademicYearSemesterMutation
from src.modules.by_law.apis import ByLawQuery, ByLawMutation
from src.modules.course.apis import CourseQuery, CourseMutation
from src.modules.course_allocation.apis import CourseAllocationQuery, CourseAllocationMutation
from src.modules.course_category.apis import CourseCategoryQuery, CourseCategoryMutation
from src.modules.course_learn_outcome.apis import CourseLearnOutcomeQuery, CourseLearnOutcomeMutation
from src.modules.course_learn_outcome_student_assessment.apis import CourseLearnOutcomeStudentAssessmentMutation, \
    CourseLearnOutcomeStudentAssessmentQuery
from src.modules.exam_category.apis import ExamCategoryQuery, ExamCategoryMutation
from src.modules.exam_course_result_forwar_logs.apis import ExamCourseResultForwardLogsQuery
from src.modules.exam_coursework.apis import ExamCourseWorkResultQuery
# from src.modules.exam_category_groups.apis import ExamCategoryGroupsQuery, ExamCategoryGroupsMutation
from src.modules.exam_result_summary.apis import ExamResultSummaryQuery, ExamResultSummaryMutation
from src.modules.exam_results.apis import ExamResultQuery, ExamResultMutation
from src.modules.groups.apis import GroupQuery, GroupMutation
from src.modules.intention_to_submit.apis import IntentionToSubmitQuery, IntentionToSubmitMutation
from src.modules.intention_to_submit_requirement.apis import IntentionToSubmitRequirementQuery, \
    IntentionToSubmitRequirementMutation
from src.modules.moodle_api_calls.apis import MoodleApiCallQuery
from src.modules.program_capacity.apis import ProgramCapacityMutation, ProgramCapacityQuery
from src.modules.program_category.apis import ProgramCategoryQuery, ProgramCategoryMutation
from src.modules.program_course.apis import ProgramCourseQuery, ProgramCourseMutation
from src.modules.program_course_assessment.apis import ProgramCourseAssessmentQuery, ProgramCourseAssessmentMutation
from src.modules.program_course_student_assessment.apis import ProgramCourseStudentAssessmentQuery, \
    ProgramCourseStudentAssessmentMutation
from src.modules.program_semester.apis import ProgramSemesterQuery, ProgramSemesterMutation
from src.modules.programs.apis import ProgramQuery, ProgramMutation
from src.modules.semester_registration.apis import SemesterRegistrationQuery
from src.modules.seminar_types.apis import SeminarTypeQuery, SeminarTypeMutation
from src.modules.sr2_api_calls.apis import Sr2ApiCallQuery, Sr2ApiCallMutation
from src.modules.states.apis import StateQuery, StateMutation
from src.modules.student.apis import StudentQuery, StudentMutation
from src.modules.student_manuscript.apis import StudentManuscriptQuery, StudentManuscriptMutation
from src.modules.student_program_change.apis import StudentProgramChangeMutation, StudentProgramChangeCourseQuery
from src.modules.student_program_change_status.apis import StudentProgramChangeStatusQuery, \
    StudentProgramChangeStatusMutation
from src.modules.student_seminar.apis import StudentSeminarQuery, StudentSeminarMutation
from src.modules.transition_metas.apis import TransitionMetaMutation, TransitionMetaQuery
from src.modules.upload_result_deadline.apis import UploadResultDeadlineQuery, UploadResultDeadlineMutation
from src.modules.workflows.apis import WorkflowQuery, WorkflowMutation


@strawberry.type
class ApiQuery(StudentQuery, ProgramCategoryQuery, CourseQuery, CourseAllocationQuery,
               CourseCategoryQuery, GroupQuery, ProgramQuery, ExamCategoryQuery,
               ExamResultSummaryQuery, ExamResultQuery,
               AcademicYearQuery, ProgramSemesterQuery, CourseLearnOutcomeQuery, ProgramCourseQuery,
               ProgramCapacityQuery, ProgramCourseAssessmentQuery, SemesterRegistrationQuery, Sr2ApiCallQuery,
               AcademicYearSemesterQuery, MoodleApiCallQuery, StudentProgramChangeCourseQuery,
               StudentProgramChangeStatusQuery, WorkflowQuery, StateQuery, TransitionMetaQuery, SeminarTypeQuery,
               StudentSeminarQuery,ByLawQuery, ExamCourseWorkResultQuery, StudentManuscriptQuery, IntentionToSubmitQuery,
               IntentionToSubmitRequirementQuery, UploadResultDeadlineQuery, ExamCourseResultForwardLogsQuery,
               ProgramCourseStudentAssessmentQuery, CourseLearnOutcomeStudentAssessmentQuery):
    pass


@strawberry.type
class ApiMutation(ProgramCategoryMutation, CourseMutation, CourseAllocationMutation,
                  CourseCategoryMutation, GroupMutation,
                  ExamCategoryMutation, AcademicYearMutation,
                  ProgramSemesterMutation, CourseLearnOutcomeMutation, ProgramCourseMutation, ProgramMutation,
                  ProgramCapacityMutation, ProgramCourseAssessmentMutation, Sr2ApiCallMutation, StudentMutation,
                  AcademicYearSemesterMutation, StudentProgramChangeMutation, StudentProgramChangeStatusMutation,
                  WorkflowMutation, StateMutation, TransitionMetaMutation, SeminarTypeMutation, StudentSeminarMutation, ByLawMutation,
                  StudentManuscriptMutation, IntentionToSubmitMutation, IntentionToSubmitRequirementMutation,
                  ExamResultSummaryMutation, ExamResultMutation, UploadResultDeadlineMutation,
                  ProgramCourseStudentAssessmentMutation, CourseLearnOutcomeStudentAssessmentMutation):
    pass
