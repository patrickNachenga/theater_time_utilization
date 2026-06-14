from typing import List
import pandas as pd
import io
import base64

from src.modules import CRUDBase
from src.models import DeathReason
from src.modules.death_reason.types import DeathReasonInput, DeathReasonListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.shared.excel_types import Base64ExcelOutput


class DeathReasonService(CRUDBase[DeathReason, DeathReasonInput, DeathReasonInput]):
    def register(self, inputs: List[DeathReasonInput]) -> Response[DeathReasonListNode]:
        try:
            result = self.create_or_update('name', inputs, DeathReasonListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=DeathReasonListNode(items=[], total_count=0))

    def import_from_excel(self, base64_data: str) -> Response[DeathReasonListNode]:
        try:
            decoded_data = base64.b64decode(base64_data)
            df = pd.read_excel(io.BytesIO(decoded_data))

            inputs = []
            for index, row in df.iterrows():
                inputs.append(DeathReasonInput(
                    name=row['name'],
                    code=row['code'] if 'code' in row and pd.notna(row['code']) else None
                ))
            return self.register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to import death reasons from excel: {e}",
                            data=DeathReasonListNode(items=[], total_count=0))

    def download_template(self) -> Response[Base64ExcelOutput]:
        try:
            template_data = {
                'name': ['Haemorrhage', 'Sepsis'],
                'code': ['DR01', 'DR02']
            }
            df = pd.DataFrame(template_data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Death Reasons')
            output.seek(0)
            encoded_data = base64.b64encode(output.read()).decode('utf-8')
            return Response(status=True, code=ResponseCode.SUCCESS, message="Template generated",
                            data=Base64ExcelOutput(file_name="death_reason_template.xlsx", base64_data=encoded_data))
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to generate template: {e}",
                            data=Base64ExcelOutput(file_name="", base64_data=""))


DeathReasonCrud = DeathReasonService(DeathReason)