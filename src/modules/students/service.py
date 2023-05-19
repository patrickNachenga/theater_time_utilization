from typing import List
from sqlalchemy import select
from src.db.session import session_scope
from src.models.student import Student
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentInput, StudentNode


class StudentService(object):
    @staticmethod
    def get_students() -> List[Student]:
        with session_scope() as session:
            result = session.query(
                Student.id,
                Student.reg_no,
                Student.created_at,
                Student.updated_at,
            ).filter(Student.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_students_by_reg_nos(reg_nos: List[str]) -> List[Student]:
        """
            Get Students by reg_nos
        :return:
        """
        with session_scope() as session:
            stmt = select(Student).where((Student.reg_no.in_(reg_nos)) & (Student.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_student_by_reg_no(reg_no: str) -> Student:
        """
            Get User by reg_no
        :param reg_no:
        :return:
        """
        with session_scope() as session:
            stmt = select(Student).where((Student.reg_no == reg_no) & (Student.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_students(self, inputs: List[StudentInput]) -> Response[List[StudentNode]]:
        """
        Register Students
        :param inputs:
        :return:
        """
        student_list = []
        with session_scope() as session:
            # Check if student already exist using reg_no
            existed_student_list = self.get_students_by_reg_nos(
                [student.reg_no for student in inputs if student.uid is None])
            if existed_student_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_student_list,
                                message="Student Already exist")

            # create new students
            for item in inputs:
                student = Student(reg_no=item.reg_no)
                student_list.append(student)

            session.add_all(student_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=student_list,
                            message="Successfully Submitted")
