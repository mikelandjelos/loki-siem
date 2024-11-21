from pydantic import BaseModel

from .input import LogInput
from .output import LogOutput


class LogGeneratorConfig(BaseModel):
    label: str
    input: LogInput
    outputs: list[LogOutput]


class GlobalConfig(BaseModel):
    generator_configs: list[LogGeneratorConfig]
