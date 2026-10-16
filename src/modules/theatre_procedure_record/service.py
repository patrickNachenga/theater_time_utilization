from datetime import datetime
from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.strategies import SelectInLoader

from src.core.security import Info
from src.database.session import session_scope
from src.modules import CRUDBase
from src.models import TheatreProcedureRecord, TheatreRecordDelay, TheatreRecordTeamMember, ExternalSource, \
    ProcedureDelayCause, TheatreProcedureRecordProcedure
from src.modules.death_reason.service import DeathReasonCrud
from src.modules.procedure_delay_cause.service import ProcedureDelayCauseCrud
from src.modules.theatre_member.service import TheatreMemberCrud
from src.modules.theatre_procedure_record.types import TheatreProcedureRecordInput, TheatreTimeRecordListNode, \
    TheatreProcedureRecordDTO, TheatreProcedureRecordNode, PreviousCaseGapNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.modules.region.service import RegionCrud
from src.modules.internal_source.service import InternalSourceCrud
from src.modules.external_source.service import ExternalSourceCrud
from src.modules.theatre_unit.service import TheatreUnitCrud
from src.modules.theatre_room.service import TheatreRoomCrud
from src.modules.procedure.service import ProcedureCrud
from src.modules.theatre_time_setting.service import TheatreTimeSettingCrud
from dataclasses import fields


def _time_to_minutes(t) -> int:
    return t.hour * 60 + t.minute


class TheatreTimeRecordService(
    CRUDBase[TheatreProcedureRecord, TheatreProcedureRecordInput, TheatreProcedureRecordInput]):
    from sqlalchemy.orm import joinedload, selectinload

    from sqlalchemy.orm import joinedload, selectinload

    @staticmethod
    def _compute_had_delay(inputs: TheatreProcedureRecordInput) -> bool:
        """
        'Was there any delay?' is never answered directly by the user — it is
        derived from the Delay & Outcome branch the user is in:

        - First case of the day: delay is inferred from the timing setup —
          the case is late if (procedure_start_time - room_preparation_minutes
          - patient_induction_minutes) falls after the configured
          start_cutting_time.
        - Any other case: delay mirrors "Did the surgery meet the time
          between cases?" (surgery_met_time_between_cases == True means a
          delay occurred relative to the previous case).
        """
        if inputs.is_first_case_of_day:
            setting = TheatreTimeSettingCrud.get_current()
            if not setting or not inputs.procedure_start_time:
                return False
            try:
                start = datetime.strptime(inputs.procedure_start_time, "%H:%M")
            except ValueError:
                return False

            ready_minutes = (
                start.hour * 60 + start.minute
                - (setting.room_preparation_minutes or 0)
                - (setting.patient_induction_minutes or 0)
            )
            cutting_minutes = _time_to_minutes(setting.start_cutting_time)
            return ready_minutes > cutting_minutes

        return bool(inputs.surgery_met_time_between_cases)

    @staticmethod
    def get_previous_case_gap(theatre_unit_uid: str, theatre_room_uid: str, procedure_date: str,
                              procedure_start_time: str, exclude_uid: str = None) -> PreviousCaseGapNode:
        """
        Looks up the most recent earlier case in the same Theatre Unit + Room
        to help answer "Did the surgery meet the time between cases?". The
        required turnaround (room prep + patient induction) mirrors the same
        global TheatreTimeSetting used by _compute_had_delay for the first
        case of the day, rather than inventing a second formula.
        """
        not_comparable = PreviousCaseGapNode(
            found=False, previous_end_time=None, previous_procedure_names=None,
            gap_minutes=None, required_minutes=None, suggested_had_delay=None,
        )
        if not theatre_unit_uid or not theatre_room_uid or not procedure_date or not procedure_start_time:
            return not_comparable

        theatre_unit = TheatreUnitCrud.get(theatre_unit_uid)
        theatre_room = TheatreRoomCrud.get(theatre_room_uid)
        if not theatre_unit or not theatre_room:
            return not_comparable

        try:
            given_date = datetime.strptime(procedure_date, "%Y-%m-%d").date()
            given_start = datetime.strptime(procedure_start_time, "%H:%M").time()
        except ValueError:
            return not_comparable

        with session_scope() as session:
            query = (
                session.query(TheatreProcedureRecord)
                .filter(
                    TheatreProcedureRecord.theatre_unit_id == theatre_unit.id,
                    TheatreProcedureRecord.theatre_room_id == theatre_room.id,
                    TheatreProcedureRecord.deleted_at.is_(None),
                    TheatreProcedureRecord.procedure_date <= given_date,
                )
            )
            if exclude_uid:
                query = query.filter(TheatreProcedureRecord.uid != exclude_uid)

            candidates = query.order_by(
                TheatreProcedureRecord.procedure_date.desc(),
                TheatreProcedureRecord.procedure_end_time.desc(),
            ).limit(5).all()

            previous = next(
                (
                    record for record in candidates
                    if record.procedure_date < given_date
                    or (record.procedure_date == given_date and record.procedure_end_time <= given_start)
                ),
                None,
            )

            if not previous:
                return not_comparable

            procedure_names = ", ".join(
                rp.procedure.name for rp in previous.procedures if rp.procedure
            ) or (previous.procedure.name if previous.procedure else None)

            if previous.procedure_date != given_date:
                return PreviousCaseGapNode(
                    found=True, previous_end_time=previous.procedure_end_time.strftime("%H:%M"),
                    previous_procedure_names=procedure_names, gap_minutes=None,
                    required_minutes=None, suggested_had_delay=None,
                )

            setting = TheatreTimeSettingCrud.get_current()
            required_minutes = None
            suggested_had_delay = None
            if setting:
                required_minutes = (setting.room_preparation_minutes or 0) + (setting.patient_induction_minutes or 0)

            gap_minutes = _time_to_minutes(given_start) - _time_to_minutes(previous.procedure_end_time)
            if required_minutes is not None:
                suggested_had_delay = gap_minutes < required_minutes

            return PreviousCaseGapNode(
                found=True,
                previous_end_time=previous.procedure_end_time.strftime("%H:%M"),
                previous_procedure_names=procedure_names,
                gap_minutes=gap_minutes,
                required_minutes=required_minutes,
                suggested_had_delay=suggested_had_delay,
            )

    @staticmethod
    async def get_by_uid(uid: str) -> Response[TheatreProcedureRecordNode]:
        """
        Get Theatre Procedure Record by UID with all related data.
        """
        with session_scope() as session:
            try:
                record = (
                    session.query(TheatreProcedureRecord)
                    .options(
                        # Direct relationships
                        joinedload(TheatreProcedureRecord.patient_region),
                        joinedload(TheatreProcedureRecord.internal_source),
                        joinedload(TheatreProcedureRecord.external_source)
                        .joinedload(ExternalSource.region),
                        joinedload(TheatreProcedureRecord.theatre_unit),
                        joinedload(TheatreProcedureRecord.theatre_room),
                        joinedload(TheatreProcedureRecord.procedure),
                        joinedload(TheatreProcedureRecord.discharge_destination),
                        joinedload(TheatreProcedureRecord.death_reason),

                        # Procedures performed in this case
                        selectinload(TheatreProcedureRecord.procedures)
                        .joinedload(TheatreProcedureRecordProcedure.procedure),

                        # Team members -> theatre member
                        selectinload(TheatreProcedureRecord.team_members)
                        .joinedload(TheatreRecordTeamMember.theatre_member),

                        # Delay records -> cause -> category
                        selectinload(TheatreProcedureRecord.delay_courses)
                        .joinedload(TheatreRecordDelay.cause)
                        .joinedload(ProcedureDelayCause.procedure_delay_category),
                    )
                    .filter(TheatreProcedureRecord.uid == uid)
                    .first()
                )

                if not record:
                    return Response(
                        status=False,
                        code=ResponseCode.NO_RECORD_FOUND,
                        message="Theatre Procedure Record not found",
                        data=None,
                    )

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Theatre Procedure Record retrieved successfully",
                    data=record,
                )

            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Unable to retrieve record",
                    data=None,
                )

    def register(self, inputs: TheatreProcedureRecordInput, info: Optional[Info] = None) -> Response[TheatreTimeRecordListNode]:
        with session_scope() as session:
            try:
                username = self._get_user_name(info)
                computed_had_delay = self._compute_had_delay(inputs)

                if inputs.uid is not None:
                    procedure_record = self.get(inputs.uid)
                    if not procedure_record:
                        return Response(status=False, code=ResponseCode.FAILURE,
                                        message="Sorry We Unable to Read Procedure Data",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0)
                                        )
                    obj_data = jsonable_encoder(inputs)
                    obj_data.pop("uid")
                    # Relationship collections are rebuilt explicitly below (clear + re-append
                    # of real mapped objects) - a raw list of dicts assigned here would corrupt
                    # the ORM collection.
                    obj_data.pop("procedures", None)
                    for key, value in obj_data.items():
                        setattr(procedure_record, key, value)
                    procedure_record.had_delay = computed_had_delay
                    procedure_record.updated_by = username
                else:
                    dto_fields = {f.name for f in fields(TheatreProcedureRecordDTO)}
                    procedure_record = TheatreProcedureRecord(
                        **{
                            field_name: field_value
                            for field_name, field_value in vars(inputs).items()
                            if field_name in dto_fields
                        }
                    )
                    procedure_record.had_delay = computed_had_delay
                    procedure_record.created_by = username



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

                if inputs.theatre_room_uid:
                    theatre_room = TheatreRoomCrud.get(inputs.theatre_room_uid)
                    if not theatre_room:
                        return Response(status=False, code=ResponseCode.FAILURE,
                                        message=f"Theatre Room not found.",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0))
                    procedure_record.theatre_room_id = theatre_room.id

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

                # Procedures performed in this case. A case can list several -
                # the combined estimate (used to judge "exceeded estimated
                # time?") is computed here server-side, same as had_delay,
                # rather than trusted from the client.
                if inputs.procedures:
                    procedure_record.procedures.clear()
                    total_estimated_minutes = 0
                    for idx, procedure_input in enumerate(inputs.procedures):
                        procedure = ProcedureCrud.get(procedure_input.procedure_uid)
                        if not procedure:
                            return Response(status=False, code=ResponseCode.FAILURE,
                                            message=f"Procedure not found.",
                                            data=TheatreTimeRecordListNode(items=[], total_count=0))
                        estimated_minutes = procedure_input.estimated_minutes
                        if estimated_minutes is None:
                            estimated_minutes = procedure.estimated_minutes
                        total_estimated_minutes += estimated_minutes or 0
                        procedure_record.procedures.append(
                            TheatreProcedureRecordProcedure(
                                procedure_id=procedure.id,
                                estimated_minutes=estimated_minutes,
                                rank=idx + 1,
                                created_by=username,
                                updated_by=username,
                            )
                        )
                        if idx == 0:
                            procedure_record.procedure_id = procedure.id
                    procedure_record.estimated_duration_minutes = total_estimated_minutes
                    if procedure_record.duration_minutes is not None:
                        procedure_record.variance_minutes = procedure_record.duration_minutes - total_estimated_minutes

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
                                created_by=username,
                                updated_by=username
                            )
                        )

                # Delay Causes — only meaningful when had_delay is actually true.
                # If the recomputed answer is "no delay", drop any previously
                # attached delay causes (e.g. an edit that flips the answer).
                if inputs.delay_courses is not None or not computed_had_delay:
                    procedure_record.delay_courses.clear()
                if computed_had_delay and inputs.delay_courses:
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
                                created_by=username,
                                updated_by = username
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
