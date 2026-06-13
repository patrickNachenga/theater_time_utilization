from typing import List
from src.modules import CRUDBase
from src.models import TheatreProcedureRecord
from src.modules.theatre_procedure_record.types import TheatreProcedureRecordInput, TheatreTimeRecordListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.modules.region.service import RegionCrud
from src.modules.internal_source.service import InternalSourceCrud
from src.modules.external_source.service import ExternalSourceCrud
from src.modules.theatre_unit.service import TheatreUnitCrud
from src.modules.procedure.service import ProcedureCrud


class TheatreTimeRecordService(CRUDBase[TheatreProcedureRecord, TheatreProcedureRecordInput, TheatreProcedureRecordInput]):
    def register(self, inputs: List[TheatreProcedureRecordInput]) -> Response[TheatreTimeRecordListNode]:
        try:
            processed_inputs = []
            for input_obj in inputs:
                new_input_obj = input_obj.copy() # Create a copy to avoid modifying the original input

                if new_input_obj.patient_region_uid:
                    region = RegionCrud.get(new_input_obj.patient_region_uid)
                    if not region:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"Patient Region with UID {new_input_obj.patient_region_uid} not found.",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0))
                    new_input_obj.patient_region_id = region.id
                    new_input_obj.patient_region_uid = None

                if new_input_obj.internal_source_uid:
                    internal_source = InternalSourceCrud.get(new_input_obj.internal_source_uid)
                    if not internal_source:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"Internal Source with UID {new_input_obj.internal_source_uid} not found.",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0))
                    new_input_obj.internal_source_id = internal_source.id
                    new_input_obj.internal_source_uid = None

                if new_input_obj.external_source_uid:
                    external_source = ExternalSourceCrud.get(new_input_obj.external_source_uid)
                    if not external_source:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"External Source with UID {new_input_obj.external_source_uid} not found.",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0))
                    new_input_obj.external_source_id = external_source.id
                    new_input_obj.external_source_uid = None

                if new_input_obj.theatre_unit_uid:
                    theatre_unit = TheatreUnitCrud.get(new_input_obj.theatre_unit_uid)
                    if not theatre_unit:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"Theatre Unit with UID {new_input_obj.theatre_unit_uid} not found.",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0))
                    new_input_obj.theatre_unit_id = theatre_unit.id
                    new_input_obj.theatre_unit_uid = None

                if new_input_obj.procedure_uid:
                    procedure = ProcedureCrud.get(new_input_obj.procedure_uid)
                    if not procedure:
                        return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                        message=f"Procedure with UID {new_input_obj.procedure_uid} not found.",
                                        data=TheatreTimeRecordListNode(items=[], total_count=0))
                    new_input_obj.procedure_id = procedure.id
                    new_input_obj.procedure_uid = None

                processed_inputs.append(new_input_obj)

            result = self.create_or_update('patient_mrn', processed_inputs, TheatreTimeRecordListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreTimeRecordListNode(items=[], total_count=0))


TheatreTimeRecordCrud = TheatreTimeRecordService(TheatreProcedureRecord)