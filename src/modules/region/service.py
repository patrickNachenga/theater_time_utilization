from typing import List
import pandas as pd
import io
import base64

from src.modules import CRUDBase
from src.models import Region
from src.modules.region.types import RegionInput, RegionListNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.shared.excel_types import Base64ExcelOutput


class RegionService(CRUDBase[Region, RegionInput, RegionInput]):
    def register(self, inputs: List[RegionInput]) -> Response[RegionListNode]:
        try:
            result = self.create_or_update('name', inputs, RegionListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=RegionListNode(items=[], total_count=0))

    def import_from_excel(self, base64_data: str) -> Response[RegionListNode]:
        try:
            decoded_data = base64.b64decode(base64_data)
            df = pd.read_excel(io.BytesIO(decoded_data))

            inputs = []
            for index, row in df.iterrows():
                inputs.append(RegionInput(
                    name=row['name'],
                    code=row['code'] if 'code' in row and pd.notna(row['code']) else None
                ))
            return self.register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to import regions from excel: {e}", data=RegionListNode(items=[], total_count=0))

    def download_template(self) -> Response[Base64ExcelOutput]:
        try:
            template_data = {
                'name': ['Sample Region 1', 'Sample Region 2'],
                'code': ['SR1', 'SR2']
            }
            df = pd.DataFrame(template_data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Regions')
            output.seek(0)
            encoded_data = base64.b64encode(output.read()).decode('utf-8')
            return Response(status=True, code=ResponseCode.SUCCESS, message="Template generated",
                            data=Base64ExcelOutput(file_name="region_template.xlsx", base64_data=encoded_data))
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to generate template: {e}",
                            data=Base64ExcelOutput(file_name="", base64_data=""))

    def get_by_code(self, field: str, attrs: List[str]) -> Response[RegionListNode]:
        """
        Fetches regions by a list of codes.
        Assumes 'code' is a unique field.
        """
        try:
            regions = self.db.query(self.model).filter(getattr(self.model, field).in_(attrs)).all()
            return Response(status=True, code=ResponseCode.SUCCESS, message="Regions fetched successfully",
                            data=RegionListNode(items=regions, total_count=len(regions)))
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE,
                            message=f"Failed to fetch regions by code: {e}",
                            data=RegionListNode(items=[], total_count=0))


RegionCrud = RegionService(Region)