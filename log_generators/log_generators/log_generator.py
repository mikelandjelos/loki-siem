import time
from logging import (
    INFO,
    FileHandler,
    Handler,
    Logger,
    NullHandler,
    StreamHandler,
    getLogger,
)
from logging.handlers import DatagramHandler, HTTPHandler, SocketHandler, SysLogHandler
from multiprocessing import Pool, cpu_count
from os.path import abspath, exists
from typing import Any, Dict, List, Tuple, Type, Unpack

from dotenv import dotenv_values

from .config_util import bootstrap_dotenv
from .log_parser import parse_logs

HANDLER_SWITCH: Dict[str, Type[Handler]] = {
    "Null": NullHandler,
    "Stream": StreamHandler,
    "File": FileHandler,
    "Socket": SocketHandler,
    "Datagram": DatagramHandler,
    "SysLog": SysLogHandler,
    "Http": HTTPHandler,
}


def __add_handlers(logger: Logger, destinations: List[Tuple[str, Unpack[Tuple[Any]]]]):
    for typeof_handler, *arguments in destinations:
        handler_class: Type[Handler] = HANDLER_SWITCH[typeof_handler]

        logger.addHandler(handler_class(*arguments))


def generate_logs(args: Tuple[str, List[Tuple[str, Any]]]):
    filename, destinations = args
    abspath_filename = abspath(filename)

    if not exists(abspath_filename):
        raise ValueError(f"File `{abspath_filename}` doesn't exist.")

    logger = getLogger(f"`{__name__}`.`{filename}`")
    logger.setLevel(INFO)

    __add_handlers(logger, destinations)

    for log in parse_logs(filename, encoding="utf-8-sig"):
        logger.info(log)
        time.sleep(1)


def start_generators(num_proc: int | None = None):
    bootstrap_dotenv()
    log_files = filter(None, dotenv_values().values())

    arguments: List[Tuple[str, List[Tuple[str, Any]]]] = [
        (
            filename,
            [
                ("File", ("./trash/data.json")),
                ("Stream", "stdout"),
            ],
        )
        for filename in log_files
    ]  # TODO - Different files, different methods.

    with Pool(num_proc or min(cpu_count(), len(arguments))) as pool:
        pool.map(generate_logs, arguments)


__all__ = [
    "generate_logs",
    "start_generators",
]
