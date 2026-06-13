import strawberry
from typing import Optional


@strawberry.input
class Base64ExcelInput:
    file_name: str
    base64_data: str


@strawberry.type
class Base64ExcelOutput:
    file_name: str
    base64_data: str