from typing import Literal
from pydantic import BaseModel
class ExportQuery(BaseModel): format: Literal["csv", "excel", "pdf"] = "csv"
