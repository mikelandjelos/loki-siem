import logging
from logging import Handler, Logger, getLogger
from multiprocessing import Pool, cpu_count
from os.path import abspath, exists
from typing import Type

import dill

from .parsers import parse_logfile
from .types import LOGGING_HANDLERS, LogGeneratorConfig, LogOutput


def __add_handlers(logger: Logger, outputs: list[LogOutput]):
    for output in outputs:
        handler_type: Type[Handler] = LOGGING_HANDLERS[output.type]
        logger.addHandler(handler_type(**output.arguments))


def generate_logs(config_pickled: bytes):
    config: LogGeneratorConfig = dill.loads(config_pickled)  # type: ignore
    assert isinstance(config, LogGeneratorConfig)

    input_file_path = abspath(config.input_logfile)

    if not exists(input_file_path):
        raise ValueError(f"File `{input_file_path}` doesn't exist.")

    logging.basicConfig(level=logging.INFO)

    logger = getLogger(config.label)
    __add_handlers(logger, config.outputs)

    for log in parse_logfile(
        input_file_path,
        timestamp_label=config.timestamp_info.label,
        timestamp_format=config.timestamp_info.format,
        encoding="utf-8-sig",
    ):
        logger.info(log)


def start_generators(
    configs: list[LogGeneratorConfig],
    num_proc: int | None = None,
):
    with Pool(num_proc or min(cpu_count(), len(configs))) as pool:
        pool.map(generate_logs, [dill.dumps(config) for config in configs])  # type: ignore
