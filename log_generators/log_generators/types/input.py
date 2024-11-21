# input.reverse_order = true

from pydantic import BaseModel


class LogTimestampInfo(BaseModel):
    label: str = "timestamp"
    format: str = "iso8601"


class LogInput(BaseModel):
    path: str
    timestamp_info: LogTimestampInfo
    reverse_order: bool = False
