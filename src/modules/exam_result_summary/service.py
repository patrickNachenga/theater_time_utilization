from typing import List

from src.db.session import session_scope
from src.helpers.utils import can_progress
from src.models import ExamResultSummary, Process, Workflow, State, ProcessFlow
from src.modules import CRUDBase
from src.types import ExamResultSummaryInput, ExamResultSummarySearchCriteria


class ExamResultSummaryService((CRUDBase[ExamResultSummary, ExamResultSummaryInput, ExamResultSummaryInput])):
    @staticmethod
    def get_exam_result_summaries(search_criteria: ExamResultSummarySearchCriteria) -> List[ExamResultSummary]:
        with session_scope() as session:
            query = session.query(ExamResultSummary).filter(ExamResultSummary.deleted_at.is_(None))

            if search_criteria.gender:
                query = query.filter(ExamResultSummary.gender == search_criteria.gender)
            if search_criteria.program_course_id:
                query = query.filter(ExamResultSummary.program_course_id == search_criteria.program_course_id)
            if search_criteria.student_uid:
                query = query.filter(ExamResultSummary.student_uid == search_criteria.student_uid)
            if search_criteria.registration_number:
                query = query.filter(ExamResultSummary.registration_number == search_criteria.registration_number)
            if search_criteria.course_code:
                query = query.filter(ExamResultSummary.course_code == search_criteria.course_code)
            if search_criteria.academic_year_uid:
                query = query.filter(ExamResultSummary.academic_year_uid == search_criteria.academic_year_uid)
            if search_criteria.program_uid:
                query = query.filter(ExamResultSummary.program_uid == search_criteria.program_uid)
            if search_criteria.course_category:
                query = query.filter(ExamResultSummary.course_category == search_criteria.course_category)
            if search_criteria.semester:
                query = query.filter(ExamResultSummary.semester == search_criteria.semester)

            # Execute the final query
            results = query.all()
            return results

    @staticmethod
    def get_student_exam_result_summaries(student_uid: str) -> List[ExamResultSummary]:
        with session_scope() as session:
            result = session.query(ExamResultSummary).filter(ExamResultSummary.student_uid == student_uid,
                                                             ExamResultSummary.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def change_result_stage(result_summary_uid: str, stage: str) -> bool:
        # check stage validit

        with session_scope() as session:

            process = session.query(Process).filter(Process.process_unique_uid == result_summary_uid).first()
            state = session.query(State).filter(State.label == stage).first()

            if can_progress(session, process, state):
                # update result summary exam status
                session.query(ExamResultSummary).filter(ExamResultSummary.uid == result_summary_uid).update(
                    {"exam_status": stage})
                # create process if it does not exist
                if process is None:
                    work_flow = session.query(Workflow).filter(Workflow.name == 'EXAM_FORWARDING').first()
                    process = Process(
                        process_unique_uid=result_summary_uid,
                        workflow=work_flow,
                        description='EXAM_FORWARDING'
                    )
                    session.add(process)
                    session.commit()
                # crate process flow progress
                process_flow = ProcessFlow(
                    state=state,
                    process=process
                )
                session.add(process_flow)
                session.commit()
                return True
            else:
                return False

    def change_program_course_result_stage(self, program_course_id: str, stage: str):
        with session_scope() as session:
            result_summaries = session.query(ExamResultSummary).filter(
                ExamResultSummary.program_course_id == program_course_id).all()
            for result_summary in result_summaries:
                self.change_result_stage(result_summary.uid, stage)
        return True


ExamResultSummaryCrud = ExamResultSummaryService(ExamResultSummary)
