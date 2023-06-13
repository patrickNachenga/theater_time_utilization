from typing import List

import pendulum
from sqlalchemy import select

from src.db.session import session_scope
from src.models.exam_result import ExamResult
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamResultsInput, ExamResultsNode


class ExamResultsService(object):
    @staticmethod
    def get_exam_results() -> List[ExamResult]:
        with session_scope() as session:
            result = session.query(
                ExamResult.id,
                ExamResult.student_id,
                ExamResult.program_course_id,
                ExamResult.exam_cat_id,
                ExamResult.publish,
                ExamResult.score,
                ExamResult.assess_no,
                ExamResult.out_of,
                ExamResult.weight,
                ExamResult.status,
                ExamResult.created_at,
                ExamResult.updated_at,
            ).filter(ExamResult.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_exam_results_by_ids(ids: List[str]) -> List[ExamResult]:
        """
        Get exam_results by ids
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamResult).where((ExamResult.id.in_(ids)) & (ExamResult.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_exam_results_id(id: int) -> ExamResult:
        """
        Get exam_results by id
        :param id:
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamResult).where((ExamResult.id == id) & (ExamResult.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_exam_results(self, inputs: List[ExamResultsInput]) -> Response[List[ExamResultsNode]]:
        """
        Save Exam Results
        :param inputs:
        :return:
        """
        exam_results_list = []
        with session_scope() as session:
            # Check if exam_results already exist using id
            # existed_exam_results_list = self.get_exam_results_by_ids(
            #    [exam_results_list for exam_results in inputs if exam_results.id is None])
            # if existed_exam_results_list:
            #    return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_exam_results_list,
            #                   message="Exam Results Already Exists")

            # create new Exam Results
            existed_exam_results = self.get_exam_results_by_ids([item.uid for item in inputs])
            for item in inputs:
                exam_results = ExamResult(
                    id=item.id,
                    student_id=item.student_id,
                    program_course_id=item.program_course_id,
                    assess_no=item.assess_no,
                    exam_cat_id=item.exam_cat_id,
                    status=item.status,
                    score=item.score,
                    weight=item.weight,
                    out_of=item.out_of,
                    publish=item.publish,
                )
                exam_results_list.append(exam_results)

            session.add_all(exam_results_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=exam_results_list,
                            message="Successfully Submitted")

    @staticmethod
    def remove_exam_results(uid: str):
        """
        Remove Programme by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(ExamResult).filter_by(uid=uid).update({ExamResult.deleted_at: pendulum.now()})
            session.commit()
