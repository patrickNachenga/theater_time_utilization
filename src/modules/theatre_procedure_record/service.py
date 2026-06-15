from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from src.core.security import Info
from src.database.session import session_scope
from src.modules import CRUDBase
from src.models import TheatreProcedureRecord, TheatreRecordDelay, TheatreRecordTeamMember
from src.modules.death_reason.service import DeathReasonCrud
from src.modules.procedure_delay_cause.service import ProcedureDelayCauseCrud
from src.modules.theatre_member.service import TheatreMemberCrud
from src.modules.theatre_procedure_record.types import TheatreProcedureRecordInput, TheatreTimeRecordListNode, \
    TheatreProcedureRecordDTO
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.modules.region.service import RegionCrud
from src.modules.internal_source.service import InternalSourceCrud
from src.modules.external_source.service import ExternalSourceCrud
from src.modules.theatre_unit.service import TheatreUnitCrud
from src.modules.procedure.service import ProcedureCrud
from dataclasses import fields


class TheatreTimeRecordService(
    CRUDBase[TheatreProcedureRecord, TheatreProcedureRecordInput, TheatreProcedureRecordInput]):
    def register(self, inputs: TheatreProcedureRecordInput, info: Optional[Info] = None) -> Response[TheatreTimeRecordListNode]:
        with session_scope() as session:
            try:
                user_id = self._get_user_id(info)

                if inputs.uid is not None:
                    procedure_record = self.get(inputs.uid)
                    if not procedure_record:
                        return Response(status=False, code=ResponseCode.FAILURE,
                                        message="Sorry We Unable to Read Procedure Data",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0)
                                        )
                    obj_data = jsonable_encoder(inputs)
                    obj_data.pop("uid")
                    for key, value in obj_data.items():
                        setattr(procedure_record, key, value)
                    procedure_record.updated_by = user_id
                else:
                    dto_fields = {f.name for f in fields(TheatreProcedureRecordDTO)}
                    procedure_record = TheatreProcedureRecord(
                        **{
                            field_name: field_value
                            for field_name, field_value in vars(inputs).items()
                            if field_name in dto_fields
                        }
                    )
                    procedure_record.created_by = user_id



                if inputs.patient_region_uid:
                    region = RegionCrud.get(inputs.patient_region_uid)
                    if not region:
                        return Response(status=False, code=ResponseCode.FAILURE,
                                        message=f"You Pass Incorect Region",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0))
                    procedure_record.patient_region_id = region.id

                if inputs.internal_source_uid:
                    internal_source = InternalSourceCrud.get(inputs.internal_source_uid)
                    if not internal_source:
                        return Response(status=False, code=ResponseCode.FAILURE,
                                        message=f"Internal Source not found.",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0))
                    procedure_record.internal_source_id = internal_source.id

                if inputs.external_source_uid:
                    external_source = ExternalSourceCrud.get(inputs.external_source_uid)
                    if not external_source:
                        return Response(status=False, code=ResponseCode.FAILURE,
                                        message=f"External Source  not found.",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0))
                    procedure_record.external_source_id = external_source.id

                if inputs.theatre_unit_uid:
                    theatre_unit = TheatreUnitCrud.get(inputs.theatre_unit_uid)
                    if not theatre_unit:
                        return Response(status=False, code=ResponseCode.FAILURE,
                                        message=f"Theatre Unit  not found.",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0))
                    procedure_record.theatre_unit_id = theatre_unit.id

                if inputs.procedure_uid:
                    procedure = ProcedureCrud.get(inputs.procedure_uid)
                    if not procedure:
                        return Response(status=False, code=ResponseCode.FAILURE,
                                        message=f"Procedure  not found.",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0))
                    procedure_record.procedure_id = procedure.id

                if inputs.discharge_destination_uid:
                    if inputs.discharge_direction == 'INTERNAL':
                        destination = InternalSourceCrud.get(inputs.discharge_destination_uid)
                    else:
                        destination = ExternalSourceCrud.get(inputs.discharge_destination_uid)
                    if not destination:
                        return Response(status=False, code=ResponseCode.FAILURE,
                                        message=f"Discharge Destination Not Correct",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0))
                    procedure_record.discharge_destination_id = destination.id

                if inputs.death_reason_uid:
                    death_reason = DeathReasonCrud.get(inputs.death_reason_uid)
                    if not death_reason:
                        return Response(status=False, code=ResponseCode.FAILURE,
                                        message=f"Death Reason Not Correct",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0))
                    procedure_record.death_reason_id = death_reason.id

                session.add(procedure_record)

                # Needed to obtain procedure_record.id
                session.flush()

                # Team Members
                if inputs.team_members:
                    print("===============team_members part===============")

                    procedure_record.team_members.clear()
                    for member_input in inputs.team_members:
                        member = TheatreMemberCrud.get(member_input.member_uid)
                        if not member:
                            return Response(status=False, code=ResponseCode.FAILURE,
                                            message=f"You Have send Incorrect Member Data",
                                            data=TheatreTimeRecordListNode(items=[], total_count=0))
                        procedure_record.team_members.append(
                            TheatreRecordTeamMember(
                                theatre_member_id=member.id,
                                role=member_input.role,
                                created_by=user_id,
                                updated_by=user_id
                            )
                        )

                # Delay Causes
                if inputs.delay_courses:
                    procedure_record.delay_courses.clear()
                    for delay_input in inputs.delay_courses:
                        procedure_delay_cause = ProcedureDelayCauseCrud.get(delay_input.delay_cause_uid)
                        if not procedure_delay_cause:
                            return Response(status=False, code=ResponseCode.FAILURE,
                                            message=f"You Have send Incorrect Procedure Delay Cause Data",
                                            data=TheatreTimeRecordListNode(items=[], total_count=0))
                        procedure_record.delay_courses.append(
                            TheatreRecordDelay(
                                cause_id=procedure_delay_cause.id,
                                description=delay_input.description,
                                created_by=user_id,
                                updated_by = user_id
                            )
                        )
                session.commit()
                session.refresh(procedure_record)


                return Response(status=True, code=ResponseCode.SUCCESS,
                                data=TheatreTimeRecordListNode(items=[], total_count=0),
                                message="Successfully Submitted")
            except Exception as e:
                print(e)
                return Response(status=False, code=ResponseCode.FAILURE, message="Failed",
                                data=TheatreTimeRecordListNode(items=[], total_count=0))


TheatreTimeRecordCrud = TheatreTimeRecordService(TheatreProcedureRecord)
