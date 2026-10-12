import base64
import io
import uuid
from uuid import UUID

import pandas as pd
from typing import List, Optional

from sqlalchemy import String, cast, or_

from src.core.security import Info
from src.database.session import session_scope
from src.modules import CRUDBase
from src.models import TheatreMember, TheatreMemberRole
from src.modules.theatre_member.types import TheatreMemberInput, TheatreMemberListNode, ImportResultNode
from src.modules.theatre_member_role.types import MemberRole
from src.shared.excel_types import Base64ExcelOutput
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import PaginationInput


class TheatreMemberService(CRUDBase[TheatreMember, TheatreMemberInput, TheatreMemberInput]):
    def register(self, inputs: List[TheatreMemberInput], info: Info) -> Response[TheatreMemberListNode]:
        try:
            result = self.create_or_update('pf_number', inputs, TheatreMemberListNode, info=info)
            return result
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreMemberListNode(items=[], total_count=0))

    def get_multi_paginated_by_role(
        self,
        pagination: PaginationInput,
        role: Optional[str] = None,
    ) -> TheatreMemberListNode:
        """
        Same shape as CRUDBase.get_multi_paginated, but can additionally
        restrict results to members tagged with a given MemberRole.
        """
        with session_scope() as session:
            query = session.query(TheatreMember).filter(TheatreMember.deleted_at.is_(None))

            if role:
                query = (
                    query.join(TheatreMemberRole, TheatreMemberRole.member_id == TheatreMember.id)
                    .filter(TheatreMemberRole.role == role, TheatreMemberRole.deleted_at.is_(None))
                )

            search_q = pagination.search or ""
            if search_q:
                search_columns = ["first_name", "middle_name", "last_name", "pf_number"]
                query = query.filter(
                    or_(*[cast(getattr(TheatreMember, col), String).ilike(f"%{search_q}%") for col in search_columns])
                )

            total_count = query.count()
            query = (
                query.order_by(TheatreMember.created_at.desc())
                .limit(pagination.limit)
                .offset(pagination.offset * pagination.limit)
            )
            items = query.all()
            session.close()

            return TheatreMemberListNode(items=items, total_count=total_count)


    def import_from_excel(self, base64_data: str, info: Info, update_existing: bool = False) -> ImportResultNode:
        try:
            decoded_data = base64.b64decode(base64_data)
            df = pd.read_excel(io.BytesIO(decoded_data))

            successful_records = []
            failed_records = []
            updated_count = 0
            pending_roles = []  # (pf_number, email, MemberRole) for rows that specified a role

            from src.database.session import session_scope

            with session_scope() as session:
                for index, row in df.iterrows():
                    pf_number = str(row.get('pf_number')).strip() if pd.notna(row.get('pf_number')) else None
                    email = str(row.get('email')).strip() if pd.notna(row.get('email')) else None

                    raw_role = row.get('role')
                    role_value = str(raw_role).strip().upper() if pd.notna(raw_role) and str(raw_role).strip() else None
                    if role_value and role_value not in MemberRole.__members__:
                        failed_row = row.to_dict()
                        failed_row['fail_reason'] = (
                            f"Invalid role '{role_value}' - must be one of {', '.join(MemberRole.__members__)}"
                        )
                        failed_records.append(failed_row)
                        continue

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

                    if existing_record and update_existing and role_value:
                        # Member was uploaded before roles existed - just attach the role, don't fail the row.
                        pending_roles.append((pf_number, email, MemberRole(role_value)))
                        updated_count += 1
                    elif existing_record:
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
                        if role_value:
                            pending_roles.append((pf_number, email, MemberRole(role_value)))
            # Save successful records
            failed_file_base64 = None
            if successful_records:
                self.register(successful_records, info=info)

            # Assign roles for rows that specified one, now that the members exist
            if pending_roles:
                from src.modules.theatre_member_role.service import TheatreMemberRoleCrud
                from src.modules.theatre_member_role.types import TheatreMemberRoleInput

                with session_scope() as session:
                    seen_member_roles = set()
                    role_inputs = []
                    for pf_number, email, role in pending_roles:
                        member = None
                        if pf_number:
                            member = session.query(TheatreMember).filter(TheatreMember.pf_number == pf_number).first()
                        if not member and email:
                            member = session.query(TheatreMember).filter(TheatreMember.email == email).first()
                        if member:
                            # Excel rows can repeat the same member+role (data entry duplicates) -
                            # collapse here since TheatreMemberRoleCrud.register's dedup check can't
                            # see not-yet-flushed inserts from earlier in the same batch.
                            dedup_key = (member.uid, role)
                            if dedup_key in seen_member_roles:
                                continue
                            seen_member_roles.add(dedup_key)
                            role_inputs.append(TheatreMemberRoleInput(member_uid=member.uid, role=role))

                role_assignment_failed = False
                if role_inputs:
                    role_result = TheatreMemberRoleCrud.register(role_inputs, info=info)
                    if getattr(role_result, "status", True) is False:
                        role_assignment_failed = True

                if role_assignment_failed:
                    # Roles didn't actually get saved (e.g. the whole batch rolled back) -
                    # don't report these rows as updated.
                    updated_count = 0

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
                    updated_count=updated_count,
                    failed_records_file=failed_file_base64
                )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message=f"Failed to import theatre members from excel: {e}",
                data=ImportResultNode(successful_count=0, failed_count=0, updated_count=0, failed_records_file=None)
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
                'role': [],
            }
            df = pd.DataFrame(template_data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Theatre Team Members')
                worksheet = writer.sheets['Theatre Team Members']
                role_col = list(template_data.keys()).index('role')
                worksheet.write_comment(0, role_col, "Optional. Must be one of: NURSES, ANAESTHETISTS, SURGEONS")
                worksheet.data_validation(1, role_col, 1000, role_col, {
                    'validate': 'list',
                    'source': ['NURSES', 'ANAESTHETISTS', 'SURGEONS'],
                })
            output.seek(0)
            encoded_data = base64.b64encode(output.read()).decode('utf-8')
            return Response(status=True, code=ResponseCode.SUCCESS, message="Template generated",
                            data=Base64ExcelOutput(file_name="theatre_members_template.xlsx", base64_data=encoded_data))
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to generate template: {e}",
                            data=Base64ExcelOutput(file_name="", base64_data=""))


TheatreMemberCrud = TheatreMemberService(TheatreMember)
