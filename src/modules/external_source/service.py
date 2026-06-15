from typing import List, Dict, Optional, Set
import pandas as pd
import io
import base64

from src.modules import CRUDBase
from src.models import ExternalSource
from src.modules.external_source.types import ExternalSourceInput, ExternalSourceListNode, ExternalSourceDTO
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.shared.excel_types import Base64ExcelOutput
from src.modules.region.service import RegionCrud


class ExternalSourceService(CRUDBase[ExternalSource, ExternalSourceInput, ExternalSourceInput]):

    def _resolve_regions_batch(
        self,
        inputs: List[ExternalSourceInput],
    ) -> Response[Dict[str, Optional[str]]]:
        """
        Batch-resolve region_code and region_uid from all inputs in just 2 queries.
        Returns a mapping of input_index -> resolved region_uid (str).
        Returns a Response with error if any region is not found.
        """
        # --- Collect unique region identifiers from all inputs in one pass ---
        unique_region_codes: Set[str] = set()
        unique_region_uids: Set[str] = set()
        for idx, inp in enumerate(inputs):
            if inp.region_code:
                unique_region_codes.add(inp.region_code)
            if inp.region_uid:
                unique_region_uids.add(inp.region_uid)

        # --- Batch query 1: fetch all regions by code (single DB hit) ---
        code_to_uid: Dict[str, int] = {}
        if unique_region_codes:
            code_regions = RegionCrud.get_multi_by_attributes("code", list(unique_region_codes))
            for region in code_regions:
                code_to_uid[region.code] = int(region.id)

        # --- Batch query 2: fetch all regions by uid (single DB hit) ---
        uid_to_uid: Dict[str, int] = {}
        if unique_region_uids:
            uid_regions = RegionCrud.get_multi_by_attributes("uid", list(unique_region_uids))
            for region in uid_regions:
                uid_to_uid[str(region.uid)] = int(region.id)

        # --- Validate that all requested regions were found ---
        missing_codes = unique_region_codes - set(code_to_uid.keys())
        missing_uids = unique_region_uids - set(uid_to_uid.keys())

        if missing_codes or missing_uids:
            missing_parts = []
            if missing_codes:
                missing_parts.append(f"codes: {', '.join(sorted(missing_codes))}")
            if missing_uids:
                missing_parts.append(f"UIDs: {', '.join(sorted(missing_uids))}")
            return Response(
                status=False,
                code=ResponseCode.VALIDATION_ERROR,
                message=f"Regions not found — {'; '.join(missing_parts)}",
                data={},
            )

        # --- Build the index -> resolved region_uid mapping ---
        resolved: Dict[str, Optional[str]] = {}
        for idx, inp in enumerate(inputs):
            resolved_region_uid: Optional[str] = None
            if inp.region_code and inp.region_code in code_to_uid:
                resolved_region_uid = code_to_uid[inp.region_code]
            elif inp.region_uid and inp.region_uid in uid_to_uid:
                resolved_region_uid = uid_to_uid[inp.region_uid]
            resolved[str(idx)] = resolved_region_uid

        return Response(
            status=True, code=ResponseCode.SUCCESS,
            message="Regions resolved",
            data=resolved,
        )

    def register(self, inputs: List[ExternalSourceInput]) -> Response[ExternalSourceListNode]:
        """
        Register external sources by resolving region_code / region_uid in bulk
        (only 2 DB queries regardless of dataset size), then delegating to
        create_or_update which batches the INSERT/UPDATE in a single commit.
        """
        try:
            if not inputs:
                return Response(
                    status=True, code=ResponseCode.FAILURE,
                    message="No inputs provided",
                    data=ExternalSourceListNode(items=[], total_count=0),
                )

            # --- Step 1: Batch-resolve all regions (at most 2 queries) ---
            region_map_resp = self._resolve_regions_batch(inputs)
            if not region_map_resp.status:
                return Response(
                    status=False, code=region_map_resp.code,
                    message=region_map_resp.message,
                    data=ExternalSourceListNode(items=[], total_count=0),
                )

            resolved_map: Dict[str, Optional[str]] = region_map_resp.data

            # --- Step 2: Build DTOs with resolved region_uid ---
            processed_inputs: List[ExternalSourceDTO] = []
            for idx, inp in enumerate(inputs):
                resolved_uid = resolved_map.get(str(idx))
                processed_inputs.append(
                    ExternalSourceDTO(
                        uid=inp.uid,
                        name=inp.name,
                        code=inp.code,
                        region_id=resolved_uid
                    )
                )

            # --- Step 3: Bulk create-or-update in a single commit ---
            self.create_or_update(
                "name", processed_inputs, ExternalSourceListNode
            )
            return Response(
                status=True, code=ResponseCode.SUCCESS,
                message=f"Registerd Successful",
                data=ExternalSourceListNode(items=[], total_count=0),
            )
        except Exception as e:
            print(e)
            return Response(
                status=False, code=ResponseCode.FAILURE,
                message=f"Failed to register external sources: {e}",
                data=ExternalSourceListNode(items=[], total_count=0),
            )

    def import_from_excel(self, base64_data: str) -> Response[ExternalSourceListNode]:
        """
        Parse an Excel file (columns: name, code, region_code) and bulk-register
        all rows in a single batch.  The batch uses at most 2 DB queries for
        region resolution regardless of row count, making it safe for large datasets.
        """
        try:
            decoded_data = base64.b64decode(base64_data)
            df = pd.read_excel(io.BytesIO(decoded_data))

            # Normalize column names (strip whitespace, lowercase)
            df.columns = [str(c).strip().lower() for c in df.columns]

            if "name" not in df.columns:
                return Response(
                    status=False, code=ResponseCode.VALIDATION_ERROR,
                    message="Excel file must contain a 'name' column",
                    data=ExternalSourceListNode(items=[], total_count=0),
                )

            inputs: List[ExternalSourceInput] = []
            for index, row in df.iterrows():
                inputs.append(
                    ExternalSourceInput(
                        name=str(row["name"]).strip(),
                        code=str(row["code"]).strip() if "code" in df.columns and pd.notna(row.get("code")) else None,
                        region_code=str(row["region_code"]).strip() if "region_code" in df.columns and pd.notna(row.get("region_code")) else None,
                    )
                )

            return self.register(inputs)
        except Exception as e:
            print(e)
            return Response(
                status=False, code=ResponseCode.FAILURE,
                message=f"Failed to import external sources from excel: {e}",
                data=ExternalSourceListNode(items=[], total_count=0),
            )

    def download_template(self) -> Response[Base64ExcelOutput]:
        try:
            template_data = {
                "name": ["Regional Hospital", "District Clinic"],
                "code": ["ES01", "ES02"],
                "region_code": ["<region-code-here>", "<region-code-here>"],
            }
            df = pd.DataFrame(template_data)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="External Sources")
            output.seek(0)
            encoded_data = base64.b64encode(output.read()).decode("utf-8")
            return Response(
                status=True, code=ResponseCode.SUCCESS,
                message="Template generated",
                data=Base64ExcelOutput(
                    file_name="external_source_template.xlsx",
                    base64_data=encoded_data,
                ),
            )
        except Exception as e:
            print(e)
            return Response(
                status=False, code=ResponseCode.FAILURE,
                message=f"Failed to generate template: {e}",
                data=Base64ExcelOutput(file_name="", base64_data=""),
            )


ExternalSourceCrud = ExternalSourceService(ExternalSource)