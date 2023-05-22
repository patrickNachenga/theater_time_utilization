from typing import List

from sqlalchemy import select

from src.db.session import session_scope
from src.models.exam_summary import ExamSummary
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamSummaryInput, ExamSummaryNode


class ExamSummaryService(object):
    @staticmethod
    def get_exam_summary() -> List[ExamSummary]:
        with session_scope() as session:
            result = session.query(
                ExamSummary.id,
                ExamSummary.student_id,
                ExamSummary.program_course_id,
                ExamSummary.marks,
                ExamSummary.grade,
                ExamSummary.gp,
                ExamSummary.remarks,
                ExamSummary.status,
                ExamSummary.created_at,
                ExamSummary.updated_at,
            ).filter(ExamSummary.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_exam_summary_by_ids(ids: List[str]) -> List[ExamSummary]:
        """
        Get exam_summary by ids
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamSummary).where((ExamSummary.in_(ids)) & (ExamSummary.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_exam_summary_id(id: str) -> ExamSummary:
        """
        Get exam_summary by id
        :param id:
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamSummary).where((ExamSummary.id == id) & (ExamSummary.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_exam_summary(self, inputs: List[ExamSummaryInput]) -> Response[List[ExamSummaryNode]]:
        """
        Save Exam Results
        :param inputs:
        :return:
        """
        exam_summary_list = []
        with session_scope() as session:
            # Check if exam_summary already exist using id
            # existed_exam_summary_list = self.get_exam_summary_by_ids(
            #     [exam_summary_list for exam_summary in inputs if exam_summary.uid is None])
            # if existed_exam_summary_list:
            #     return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_exam_summary_list,
            #                     message="Exam Results Already Exists")

            # create new Exam Results
            for item in inputs:
                exam_summary = ExamSummary(
                    id=item.id,
                    student_id=item.student_id,
                    program_course_id=item.program_course_id,
                    grade=item.grade,
                    marks=item.marks,
                    remarks=item.marks,
                    gp=item.gp,
                    status=item.status,
                )
                exam_summary_list.append(exam_summary)

            session.add_all(exam_summary_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=exam_summary,
                            message="Successfully Submitted")