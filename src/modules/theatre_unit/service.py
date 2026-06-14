from typing import List
import pandas as pd
import io
import base64

from src.modules import CRUDBase
from src.models import TheatreUnit
from src.modules.theatre_unit.types import TheatreUnitInput, TheatreUnitListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.shared.excel_types import Base64ExcelOutput


class TheatreUnitService(CRUDBase[TheatreUnit, TheatreUnitInput, TheatreUnitInput]):
    def register(self, inputs: List[TheatreUnitInput]) -> Response[TheatreUnitListNode]:
        try:
            result = self.create_or_update('name', inputs, TheatreUnitListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreUnitListNode(items=[], total_count=0))

    def import_from_excel(self, base64_data: str) -> Response[TheatreUnitListNode]:
        try:
            decoded_data = base64.b64decode(base64_data)
            df = pd.read_excel(io.BytesIO(decoded_data))

            inputs = []
            for index, row in df.iterrows():
                inputs.append(TheatreUnitInput(
                    name=row['name'],
                    code=row['code'] if 'code' in row and pd.notna(row['code']) else None,
                    location=row['location'] if 'location' in row and pd.notna(row['location']) else None
                ))
            return self.register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to import theatre units from excel: {e}",
                            data=TheatreUnitListNode(items=[], total_count=0))

    def download_template(self) -> Response[Base64ExcelOutput]:
        try:
            template_data = {
                'name': ['Main Operating Theatre', 'Emergency Theatre'],
                'code': ['TU01', 'TU02'],
                'location': ['Block A, Floor 2', 'Block B, Ground Floor']
            }
            df = pd.DataFrame(template_data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Theatre Units')
            output.seek(0)
            encoded_data = base64.b64encode(output.read()).decode('utf-8')
            return Response(status=True, code=ResponseCode.SUCCESS, message="Template generated",
                            data=Base64ExcelOutput(file_name="theatre_unit_template.xlsx", base64_data=encoded_data))
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to generate template: {e}",
                            data=Base64ExcelOutput(file_name="", base64_data=""))


TheatreUnitCrud = TheatreUnitService(TheatreUnit)