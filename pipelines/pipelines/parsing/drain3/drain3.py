import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from os.path import dirname
from typing import Optional

from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

LOG_DIR = "data/misc/"
LOG_FILE = "SSH.log"

RESULTS_ROOT_DIR = os.path.join(os.path.dirname(__file__), "results")


def get_parser(parent_subparsers: Optional[argparse._SubParsersAction] = None):
    """Drain3 log parser (production ready Drain)."""
    parser = (
        argparse.ArgumentParser(description=get_parser.__doc__)
        if not parent_subparsers
        else parent_subparsers.add_parser("drain3", description=get_parser.__doc__)
    )

    parser.set_defaults(func=main)

    return parser


def main(args: Optional[argparse.Namespace] = None):
    if not os.path.exists(RESULTS_ROOT_DIR):
        os.makedirs(RESULTS_ROOT_DIR)

    if not args:
        args = get_parser().parse_args()

    config = TemplateMinerConfig()
    config.load(f"{dirname(__file__)}/drain3.ini")
    config.profiling_enabled = True
    template_miner = TemplateMiner(config=config)

    line_count = 0

    logfile_path = os.path.join(LOG_DIR, LOG_FILE)

    with open(logfile_path) as f:
        lines = f.readlines()

    start_time = time.time()
    batch_start_time = start_time
    batch_size = 10000

    for line in lines:
        line = line.rstrip()
        line = line.partition(": ")[2]
        result = template_miner.add_log_message(line)
        line_count += 1
        if line_count % batch_size == 0:
            time_took = time.time() - batch_start_time
            rate = batch_size / time_took
            logger.info(
                f"Processing line: {line_count}, rate {rate:.1f} lines/sec, "
                f"{len(template_miner.drain.clusters)} clusters so far."
            )
            batch_start_time = time.time()
        if result["change_type"] != "none":
            result_json = json.dumps(result)
            logger.info(f"Input ({line_count}): {line}")
            logger.info(f"Result: {result_json}")

    time_took = time.time() - start_time
    rate = line_count / time_took
    logger.info(
        f"--- Done processing file in {time_took:.2f} sec. Total of {line_count} lines, rate {rate:.1f} lines/sec, "
        f"{len(template_miner.drain.clusters)} clusters"
    )

    sorted_clusters = sorted(
        template_miner.drain.clusters, key=lambda it: it.size, reverse=True
    )
    for cluster in sorted_clusters:
        logger.info(cluster)

    print("Prefix Tree:")
    with open(
        os.path.join(
            RESULTS_ROOT_DIR,
            f"tree-{os.path.splitext(os.path.basename(logfile_path))}-{datetime.isoformat(datetime.now())}Z.txt",
        ),
        "wt",
    ) as f:
        template_miner.drain.print_tree(f)

    template_miner.profiler.report(0)


if __name__ == "__main__":
    main()
