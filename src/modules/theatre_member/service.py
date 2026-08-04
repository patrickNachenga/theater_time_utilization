import base64
import io
import uuid
from uuid import UUID

import pandas as pd
from typing import List

from src.core.security import Info
from src.modules import CRUDBase
from src.models import TheatreMember
from src.modules.theatre_member.types import TheatreMemberInput, TheatreMemberListNode
from src.shared.excel_types import Base64ExcelOutput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class TheatreMemberService(CRUDBase[TheatreMember, TheatreMemberInput, TheatreMemberInput]):
    def register(self, inputs: List[TheatreMemberInput]) -> Response[TheatreMemberListNode]:
        try:
            result = self.create_or_update('pf_number', inputs, TheatreMemberListNode)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreMemberListNode(items=[], total_count=0))


    def import_from_excel(self, base64_data: str, info: Info) -> Response[TheatreMemberListNode]:
        try:
            decoded_data = base64.b64decode(base64_data)
            df = pd.read_excel(io.BytesIO(decoded_data))

            inputs = []
            for index, row in df.iterrows():
                inputs.append(TheatreMemberInput(
                    user_uid=uuid.uuid4(),
                    first_name=row['first_name'] if 'first_name' in row and pd.notna(row['first_name']) else None,
                    middle_name=row['middle_name'] if 'middle_name' in row and pd.notna(row['middle_name']) else None,
                    last_name=row['last_name'] if 'last_name' in row and pd.notna(row['last_name']) else None,
                    pf_number=row['pf_number'] if 'pf_number' in row and pd.notna(row['pf_number']) else None,
                    email=row['email'] if 'email' in row and pd.notna(row['email']) else None,
                    phone_number=row['phone_number'] if 'phone_number' in row and pd.notna(row['phone_number']) else None
                ))
            return self.register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to import theatre members from excel: {e}",
                            data=TheatreMemberListNode(items=[], total_count=0))


    def download_template(self) -> Response[Base64ExcelOutput]:
        try:
            template_data = {
                'first_name': [],
                'middle_name': [],
                'last_name': [],
                'pf_number': [],
                'email': [],
                'phone_number': [],
            }
            df = pd.DataFrame(template_data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Theatre Team Members')
            output.seek(0)
            encoded_data = base64.b64encode(output.read()).decode('utf-8')
            return Response(status=True, code=ResponseCode.SUCCESS, message="Template generated",
                            data=Base64ExcelOutput(file_name="theatre_members_template.xlsx", base64_data=encoded_data))
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to generate template: {e}",
                            data=Base64ExcelOutput(file_name="", base64_data=""))


TheatreMemberCrud = TheatreMemberService(TheatreMember)
