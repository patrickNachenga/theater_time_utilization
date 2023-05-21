from typing import List

from sqlalchemy import select

from src.db.session import session_scope
from src.models.programme import Programme
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgrammeInput, ProgrammeNode


class ProgrammeService(object):
    @staticmethod
    def get_programmes() -> List[Programme]:
        with session_scope() as session:
            result = session.query(
                Programme.id,
                Programme.uid,
                Programme.code,
                Programme.name,
                Programme.short_name,
                Programme.max_student,
                Programme.tcu_code,
                Programme.programme_number,
                Programme.programme_type_id,
                Programme.created_by,
                Programme.specialization_area_id,
                Programme.institute_unit_id,
                Programme.qualification,
                Programme.action,
                Programme.created_at,
                Programme.updated_at,
            ).filter(Programme.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_programme_by_programme_numbers(programme_numbers: List[str]) -> List[Programme]:
        """
            Get programme by programme_number
        :return:
        """
        with session_scope() as session:
            stmt = select(Programme).where(
                (Programme.programme_number.in_(programme_numbers)) & (Programme.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_programme_by_uids(uids: List[str]) -> List[Programme]:
        """
            Get programmes by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(Programme).where((Programme.uid.in_(uids)) & (Programme.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_programme_by_programme_number(programme_number: str) -> Programme:
        """
        Get Programme by programme_numbers
        :param:
        :return:
        """
        with session_scope() as session:
            stmt = select(Programme).where(
                (Programme.programme_number == programme_number) & (Programme.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_get_programme(self, inputs: List[ProgrammeInput]) -> Response[List[ProgrammeNode]]:
        """
        Register Programme
        :param inputs:
        :return:
        """
        programme_list = []
        with session_scope() as session:
            # Check if programme already exist using programme_number
            existed_programme_list = self.get_programme_by_programme_numbers(
                [Programme.programme_numbers for programme in inputs if programme.uid is None])
            if existed_programme_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_programme_list,
                                message="Programme Already Exists")
            # check for existing Programme using uid
            existed_programme = self.get_programme_by_uids([item.uid for item in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    programme = Programme(
                        programme_number=inputItem.programme_number,
                        code=inputItem.code,
                        name=inputItem.name,
                        short_name=inputItem.short_name,
                        tcu_code=inputItem.tcu_code,
                        duration=inputItem.duration,
                        qualification=inputItem.qualification,
                        max_student=inputItem.max_student,
                        action=inputItem.action,
                        created_by=inputItem.created_by,
                        programme_type_id=inputItem.programme_type_id,
                        specialization_area_id=inputItem.specialization_area_id,
                        institute_unit_id=inputItem.institute_unit_id,
                    )
                    programme_list.append(programme)
                else:
                    programme = next(filter(lambda programme: str(programme.uid) == str(inputItem.uid),
                                            existed_programme), None)

                    if programme:
                        programme.programme_number = inputItem.programme_number,
                        programme.code = inputItem.code,
                        programme.name = inputItem.name,
                        programme.short_name = inputItem.short_name,
                        programme.tcu_code = inputItem.tcu_code,
                        programme.duration = inputItem.duration,
                        programme.qualification = inputItem.qualification,
                        programme.max_student = inputItem.max_student,
                        programme.action = inputItem.action,
                        programme.created_by = inputItem.created_by,
                        programme.programme_type_id = inputItem.programme_type_id,
                        programme.specialization_area_id = inputItem.specialization_area_id,
                        programme.institute_unit_id = inputItem.institute_unit_id,
                        programme_list.append(programme)
            session.add_all(programme_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=programme_list,
                            message="Successfully Submitted")
