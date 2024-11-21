from concurrent.futures import ThreadPoolExecutor
from logging import INFO, Handler, Logger, getLogger
from os.path import abspath, exists
from typing import Type

from .parsers import logfile_to_logstream
from .types import LOGGING_HANDLERS, LogGeneratorConfig, LogOutput


def __add_handlers(logger: Logger, outputs: list[LogOutput]):
    for output in outputs:
        handler_type: Type[Handler] = LOGGING_HANDLERS[output.type]
        logger.addHandler(handler_type(**output.arguments))


def generate_logs(config: LogGeneratorConfig):
    input_file_path = abspath(config.input.path)

    if not exists(input_file_path):
        raise ValueError(f"File `{input_file_path}` doesn't exist.")

    logger = getLogger(config.label)
    logger.setLevel(INFO)
    __add_handlers(logger, config.outputs)

    for log in logfile_to_logstream(
        input_file_path,
        timestamp_label=config.input.timestamp_info.label,
        timestamp_format=config.input.timestamp_info.format,
        encoding="utf-8-sig",
        reverse_order=config.input.reverse_order,
    ):
        logger.info(log)


def start_generators(
    configs: list[LogGeneratorConfig],
    num_threads: int | None = None,
):
    num_of_threads = num_threads or len(configs)
    with ThreadPoolExecutor(
        max_workers=num_of_threads,
        thread_name_prefix="generator",
    ) as executor:
        executor.map(generate_logs, configs)
