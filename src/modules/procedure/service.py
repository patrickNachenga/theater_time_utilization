import base64
import pandas as pd
import io
from typing import List
from src.modules import CRUDBase
from src.models import Procedure
from src.modules.procedure.types import ProcedureInput, ProcedureListNode
from src.shared.excel_types import Base64ExcelOutput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class ProcedureService(CRUDBase[Procedure, ProcedureInput, ProcedureInput]):
    def register(self, inputs: List[ProcedureInput]) -> Response[ProcedureListNode]:
        try:
            result = self.create_or_update('name', inputs, ProcedureListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ProcedureListNode(items=[], total_count=0))


    def import_from_excel(self, base64_data: str) -> Response[ProcedureListNode]:
        try:
            decoded_data = base64.b64decode(base64_data)
            df = pd.read_excel(io.BytesIO(decoded_data))

            inputs = []
            for index, row in df.iterrows():
                inputs.append(ProcedureInput(
                    name=row['NAME'],
                    code=row['CODE'],
                    estimated_minutes=row['ESTIMATED_MINUTES']
                ))
            return self.register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to import procedure from excel: {e}",
                            data=ProcedureListNode(items=[], total_count=0))



    def download_template(self) -> Response[Base64ExcelOutput]:
        try:
            template_data = {
                'NAME': ['Procedure Name 1', 'Procedure Name 2'],
                'CODE': ['ICD-10 Code 1', 'ICD-10 Code 2'],
                'ESTIMATED_MINUTES': ['120', '150'],
            }
            df = pd.DataFrame(template_data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Procedure Delay Categories')
            output.seek(0)
            encoded_data = base64.b64encode(output.read()).decode('utf-8')
            return Response(status=True, code=ResponseCode.SUCCESS, message="Template generated",
                            data=Base64ExcelOutput(file_name="procedure__template.xlsx", base64_data=encoded_data))
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to generate template: {e}",
                            data=Base64ExcelOutput(file_name="", base64_data=""))




ProcedureCrud = ProcedureService(Procedure)
