from typing import List
import logging

from src.modules import CRUDBase
from src.models import ProcedureDelayCause
from src.modules.procedure_delay_cause.types import (
    ProcedureDelayCauseInput,
    ProcedureDelayCauseListNode,
    ProcedureDelayCauseDTO
)
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.modules.procedure_delay_category.service import (
    ProcedureDelayCategoryCrud
)

logger = logging.getLogger(__name__)


class ProcedureDelayCauseService(CRUDBase[ProcedureDelayCause, ProcedureDelayCauseInput, ProcedureDelayCauseInput]):
    def register(self, inputs: List[ProcedureDelayCauseInput]) -> Response[ProcedureDelayCauseListNode]:
        try:
            if not inputs:
                return Response(status=False, code=ResponseCode.VALIDATION_ERROR, message="No records supplied.")

            category_uids = [
                item.procedure_delay_category_uid
                for item in inputs
                if item.procedure_delay_category_uid
            ]

            if len(category_uids) != len(inputs):
                return Response(status=False, code=ResponseCode.VALIDATION_ERROR,
                                message="Each record must contain a Valid Procedure Delay Category"
                                )


            procedure_categories = (
                ProcedureDelayCategoryCrud.get_multi_by_attributes(
                    field="uid",
                    attrs=list(set(category_uids))
                )
            )


            category_map = {
                str(category.uid): category.id
                for category in procedure_categories
            }


            processed_inputs = []

            for item in inputs:
                processed_inputs.append(
                    ProcedureDelayCauseDTO(
                        uid=item.uid,
                        name=item.name,
                        code=item.code,
                        description=item.description,
                        procedure_delay_category_id=int(category_map[str(item.procedure_delay_category_uid)])
                    )
                )

            return self.create_or_update("name", processed_inputs,ProcedureDelayCauseListNode )
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed To register",
                            data=ProcedureDelayCauseListNode(items=[], total_count=0)
                            )


ProcedureDelayCauseCrud = ProcedureDelayCauseService(ProcedureDelayCause)
