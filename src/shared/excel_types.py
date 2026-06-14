import strawberry
from typing import Optional, List


@strawberry.input
class Base64ExcelInput:
    file_name: str
    base64_data: str


@strawberry.type
class Base64ExcelOutput:
    file_name: str
    base64_data: str


@strawberry.type
class ImportResultItem:
    row: int
    status: str  # "imported" | "duplicate" | "failed"
    name: str
    message: Optional[str] = None


@strawberry.type
class ImportExcelOutput:
    total_rows: int
    imported: int
    duplicates: int
    failed: int
    details: List[ImportResultItem]
