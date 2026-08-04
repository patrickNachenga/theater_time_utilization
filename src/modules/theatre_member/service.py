import base64
import io
import uuid
from uuid import UUID

import pandas as pd
from typing import List

from src.core.security import Info
from src.modules import CRUDBase
from src.models import TheatreMember
from src.modules.theatre_member.types import TheatreMemberInput, TheatreMemberListNode, ImportResultNode
from src.shared.excel_types import Base64ExcelOutput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class TheatreMemberService(CRUDBase[TheatreMember, TheatreMemberInput, TheatreMemberInput]):
    def register(self, inputs: List[TheatreMemberInput], info: Info) -> Response[TheatreMemberListNode]:
        try:
            result = self.create_or_update('pf_number', inputs, TheatreMemberListNode, info=info)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreMemberListNode(items=[], total_count=0))


    def import_from_excel(self, base64_data: str, info: Info) -> ImportResultNode:
        try:
            decoded_data = base64.b64decode(base64_data)
            df = pd.read_excel(io.BytesIO(decoded_data))
            
            successful_records = []
            failed_records = []

            from src.database.session import session_scope
            
            with session_scope() as session:
                for index, row in df.iterrows():
                    pf_number = str(row.get('pf_number')).strip() if pd.notna(row.get('pf_number')) else None
                    email = str(row.get('email')).strip() if pd.notna(row.get('email')) else None

                    # Check if record exists by pf_number or email
                    existing_record = None
                    if pf_number:
                        existing_record = session.query(TheatreMember).filter(
                            TheatreMember.pf_number == pf_number
                        ).first()
                    
                    if not existing_record and email:
                        existing_record = session.query(TheatreMember).filter(
                            TheatreMember.email == email
                        ).first()

                    if existing_record:
                        # Record exists, add to failed
                        failed_row = row.to_dict()
                        if pf_number and email:
                            failed_row['fail_reason'] = f"Record already exists with pf_number '{pf_number}' or email '{email}'"
                        elif pf_number:
                            failed_row['fail_reason'] = f"Record already exists with pf_number '{pf_number}'"
                        else:
                            failed_row['fail_reason'] = f"Record already exists with email '{email}'"
                        failed_records.append(failed_row)
                    else:
                        # Record doesn't exist, save it
                        input_data = TheatreMemberInput(
                            user_uid=uuid.uuid4(),
                            first_name=str(row.get('first_name')).strip() if pd.notna(row.get('first_name')) else None,
                            middle_name=str(row.get('middle_name')).strip() if pd.notna(row.get('middle_name')) else None,
                            last_name=str(row.get('last_name')).strip() if pd.notna(row.get('last_name')) else None,
                            pf_number=pf_number,
                            email=email,
                            phone_number=str(row.get('phone_number')).strip() if pd.notna(row.get('phone_number')) else None
                        )
                        successful_records.append(input_data)
            # Save successful records
            failed_file_base64 = None
            if successful_records:
                self.register(successful_records, info=info)

            # Generate failed records Excel file if there are failures
            if failed_records:
                failed_df = pd.DataFrame(failed_records)
                # Ensure fail_reason column is at the end
                if 'fail_reason' in failed_df.columns:
                    cols = [col for col in failed_df.columns if col != 'fail_reason'] + ['fail_reason']
                    failed_df = failed_df[cols]
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    failed_df.to_excel(writer, index=False, sheet_name='Failed Records')
                output.seek(0)
                failed_file_base64 = base64.b64encode(output.read()).decode('utf-8')

            return ImportResultNode(
                    successful_count=len(successful_records),
                    failed_count=len(failed_records),
                    failed_records_file=failed_file_base64
                )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message=f"Failed to import theatre members from excel: {e}",
                data=ImportResultNode(successful_count=0, failed_count=0, failed_records_file=None)
            )


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
