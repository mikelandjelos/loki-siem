import logging
import os
from dataclasses import asdict
from time import perf_counter_ns

import pandas as pd
from logparser import Drain
from logparser.utils import evaluator

from .configs import CONFIGS_2K, RESULTS_ROOT_DIR, DrainConfig

__logger = logging.getLogger(__name__)


def drain_parse_benchmark(configs: dict[str, tuple[DrainConfig, str]]):
    benchmarks = []
    outdir = ""

    for config_name, (config, log_file) in configs.items():
        # Parsing.
        start = perf_counter_ns()
        parser = Drain.LogParser(**asdict(config))
        parser.parse(logName=log_file)
        end = perf_counter_ns()
        __logger.info(f"Finished parsing: `{config_name}` [{end - start/1000}us]")

        # Benchmarking.
        f1_measure, accuracy = evaluator.evaluate(
            groundtruth=os.path.join(config.indir, log_file + "_structured.csv"),
            parsedresult=os.path.join(config.outdir, log_file + "_structured.csv"),
        )
        benchmarks.append((config_name, f1_measure, accuracy))
        outdir = config.outdir

    if benchmarks and outdir:
        df_benchmark = pd.DataFrame(
            benchmarks, columns=["Dataset Name", "F1 Measure", "Accuracy"]
        )
        df_benchmark.set_index("Dataset Name", inplace=True)
        df_benchmark.to_csv(os.path.join(outdir, f"benchmark.csv"), float_format="%.6f")
        print(df_benchmark)


def main():
    __logger.setLevel(logging.INFO)

    if not os.path.exists(RESULTS_ROOT_DIR):
        os.mkdir(RESULTS_ROOT_DIR)
        os.mkdir(os.path.join(RESULTS_ROOT_DIR, "drain"))
        os.mkdir(os.path.join(RESULTS_ROOT_DIR, "drain", "loghub_2k"))

    drain_parse_benchmark(CONFIGS_2K)


if __name__ == "__main__":
    main()
