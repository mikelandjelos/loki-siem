from pydantic import BaseModel, Field

from .output import LogOutput


class LogTimestampInfo(BaseModel):
    label: str = "timestamp"
    format: str = "iso8601"


class LogGeneratorConfig(BaseModel):
    label: str
    input_logfile: str
    timestamp_info: LogTimestampInfo = Field(default_factory=LogTimestampInfo)
    outputs: list[LogOutput] = Field(default_factory=list)


class GlobalConfig(BaseModel):
    generator_configs: list[LogGeneratorConfig]
