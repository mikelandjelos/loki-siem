import os
from dataclasses import asdict

from logparser import Drain

from .apache_2k_config import APACHE_2K_CONFIG
from .apache_elfak_config import APACHE_ELFAK_CONFIG
from .common import RESULTS_ROOT_DIR, DrainConfig


def parse_logs(parser_config: DrainConfig, logfile: str):
    parser = Drain.LogParser(**asdict(parser_config))
    parser.parse(logName=logfile)


def benchmark():
    parse_logs(APACHE_2K_CONFIG, "Apache_2k.log")
    parse_logs(APACHE_ELFAK_CONFIG, "Access Logs-data-2024-10-11 10_22_32.log")


def main():
    if not os.path.exists(RESULTS_ROOT_DIR):
        os.mkdir(RESULTS_ROOT_DIR)
        os.mkdir(os.path.join(RESULTS_ROOT_DIR), "drain")

    benchmark()


if __name__ == "__main__":
    main()
