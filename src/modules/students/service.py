from typing import List
from sqlalchemy import select
from src.db.session import session_scope
from src.models.student import Student
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentInput, StudentNode
import pendulum


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
    def get_students_by_uids(uids: List[str]) -> List[Student]:
        """
        Get students by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(Student).where((Student.uid.in_(uids)) & (Student.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_student_by_reg_no(reg_no: str) -> Student:
        """
        Get student by reg_no
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
                                message="Student Already Exists")
            # check for existing staff using uid
            existed_student = self.get_students_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    student = Student(reg_no=inputItem.reg_no)
                    student_list.append(student)
                else:
                    student = next(filter(lambda student: str(student.uid) == str(inputItem.uid),
                                          existed_student), None)

                    if student:
                        student.reg_no = inputItem.reg_no
                        student_list.append(student)
            session.add_all(student_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=student_list,
                            message="Successfully Submitted")

    # Delete Function
    @staticmethod
    def remove_student(uid: str):
        """
        Remove Service by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(Student).filter_by(uid=uid).update({Student.deleted_at: pendulum.now()})
            session.commit()




