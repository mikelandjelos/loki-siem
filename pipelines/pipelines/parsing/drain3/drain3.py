import json
import logging
import os
import sys
import time
from os.path import dirname

from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")

LOG_DIR = "data/misc/"
LOG_FILE = "SSH.log"


def main():
    config = TemplateMinerConfig()
    config.load(f"{dirname(__file__)}/drain3.ini")
    config.profiling_enabled = True
    template_miner = TemplateMiner(config=config)

    line_count = 0

    with open(os.path.join(LOG_DIR, LOG_FILE)) as f:
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
    with open(os.path.join(dirname(__name__), "tree.txt"), "wt") as f:
        template_miner.drain.print_tree(f)

    template_miner.profiler.report(0)


if __name__ == "__main__":
    main()
