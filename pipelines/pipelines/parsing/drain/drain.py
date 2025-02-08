import logging
import os
from dataclasses import asdict
from time import perf_counter_ns

from logparser import Drain

from .configs import CONFIGS, RESULTS_ROOT_DIR, DrainConfig

__logger = logging.getLogger(__name__)


def parse_logs(parser_config: DrainConfig, logfile: str):
    parser = Drain.LogParser(**asdict(parser_config))
    parser.parse(logName=logfile)


def drain_parsing_benchmark(configs: dict[str, tuple[DrainConfig, str]]):
    for config_name, (config, log_file) in configs.items():
        start = perf_counter_ns()
        parse_logs(config, log_file)
        end = perf_counter_ns()
        __logger.info(f"Finished parsing: `{config_name}` [{end - start/1000}us]")


def main():
    __logger.setLevel(logging.INFO)

    if not os.path.exists(RESULTS_ROOT_DIR):
        os.mkdir(RESULTS_ROOT_DIR)
        os.mkdir(os.path.join(RESULTS_ROOT_DIR, "drain"))

    drain_parsing_benchmark(CONFIGS)


if __name__ == "__main__":
    main()
