from typing import List
import pandas as pd
import io
import base64

from src.modules import CRUDBase
from src.models import InternalSource
from src.modules.internal_source.types import InternalSourceInput, InternalSourceListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.shared.excel_types import Base64ExcelOutput


class InternalSourceService(CRUDBase[InternalSource, InternalSourceInput, InternalSourceInput]):
    def register(self, inputs: List[InternalSourceInput]) -> Response[InternalSourceListNode]:
        try:
            result = self.create_or_update('name', inputs, InternalSourceListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=InternalSourceListNode(items=[], total_count=0))

    def import_from_excel(self, base64_data: str) -> Response[InternalSourceListNode]:
        try:
            decoded_data = base64.b64decode(base64_data)
            df = pd.read_excel(io.BytesIO(decoded_data))

            inputs = []
            for index, row in df.iterrows():
                inputs.append(InternalSourceInput(
                    name=row['name'],
                    code=row['code'] if 'code' in row and pd.notna(row['code']) else None
                ))
            return self.register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to import internal sources from excel: {e}",
                            data=InternalSourceListNode(items=[], total_count=0))

    def download_template(self) -> Response[Base64ExcelOutput]:
        try:
            template_data = {
                'name': ['Theatre Register', 'Casualty Form'],
                'code': ['IS01', 'IS02']
            }
            df = pd.DataFrame(template_data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Internal Sources')
            output.seek(0)
            encoded_data = base64.b64encode(output.read()).decode('utf-8')
            return Response(status=True, code=ResponseCode.SUCCESS, message="Template generated",
                            data=Base64ExcelOutput(file_name="internal_source_template.xlsx", base64_data=encoded_data))
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to generate template: {e}",
                            data=Base64ExcelOutput(file_name="", base64_data=""))


InternalSourceCrud = InternalSourceService(InternalSource)