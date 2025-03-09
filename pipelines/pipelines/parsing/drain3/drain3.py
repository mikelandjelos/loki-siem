import argparse
import json
import logging
import os
import sys
from os.path import dirname, exists, join
from typing import Optional

from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig

from ..._util import get_dataset_name, log_generator

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

LOG_DIR = "data/misc/"
LOG_FILE = "drain3_test.log"

RESULTS_DIR = join("results", "parsing", "drain3")


def get_parser(parent_subparsers: Optional[argparse._SubParsersAction] = None):
    """Drain3 log parser."""
    parser = (
        argparse.ArgumentParser(description=get_parser.__doc__)
        if not parent_subparsers
        else parent_subparsers.add_parser("drain3", description=get_parser.__doc__)
    )

    parser.set_defaults(func=main)

    return parser


def main(args: Optional[argparse.Namespace] = None):
    if not exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    if not args:
        args = get_parser().parse_args()

    config_file = join(dirname(__file__), "drain3.ini")
    config = TemplateMinerConfig()
    config.load(config_file)
    config.profiling_enabled = True
    template_miner = TemplateMiner(config=config)

    line_count = 0

    dataset_file = join(LOG_DIR, LOG_FILE)

    logger.info("\n\tLOGS:\n")

    for line in log_generator(dataset_file):
        line = line.strip()
        result = template_miner.add_log_message(line)

        result_json = json.dumps(result)
        logger.info(f"Input ({line_count}): {line} => {result_json}")

    sorted_clusters = sorted(
        template_miner.drain.clusters,
        key=lambda it: it.size,
        reverse=True,
    )

    logger.info("\n\tCLUSTERS:\n")
    for cluster in sorted_clusters:
        logger.info(cluster)

    with open(join(RESULTS_DIR, f"{get_dataset_name(dataset_file)}.tree"), "wt") as f:
        template_miner.drain.print_tree(f)

    logger.info("\n\tREPORT:\n")
    template_miner.profiler.report(0)


if __name__ == "__main__":
    main()
