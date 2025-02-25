import argparse
import logging
import os
from dataclasses import asdict
from time import perf_counter_ns

import pandas as pd
from logparser import Drain
from logparser.utils import evaluator

from .configs import (
    CONFIGS_2K,
    CONFIGS_ELFAK,
    OUTDIR_2K,
    OUTDIR_ELFAK,
    RESULTS_ROOT_DIR,
    DrainConfig,
)

__logger = logging.getLogger(__name__)


def drain_parse(configs: dict[str, tuple[DrainConfig, str]]):
    for config_name, (config, log_file) in configs.items():
        start = perf_counter_ns()
        parser = Drain.LogParser(**asdict(config))
        parser.parse(logName=log_file)
        end = perf_counter_ns()
        __logger.info(f"Finished parsing: `{config_name}` [{end - start/1000}us]")


def drain_benchmark(configs: dict[str, tuple[DrainConfig, str]]):
    benchmarks = []
    outdir = ""

    for config_name, (config, log_file) in configs.items():
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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Log parsing and anomaly detection with benchmarking."
    )
    parser.add_argument("--benchmarks", action="store_true", help="Run benchmarks")
    parser.add_argument("--parsing", action="store_true", help="Run log parsing")
    return parser.parse_args()


def main():
    __logger.setLevel(logging.INFO)

    if not os.path.exists(RESULTS_ROOT_DIR):
        os.mkdir(RESULTS_ROOT_DIR)
        os.mkdir(os.path.join(RESULTS_ROOT_DIR, "drain"))

        os.mkdir(OUTDIR_2K)
        os.mkdir(OUTDIR_ELFAK)

    args = parse_args()

    # Benchmarking LogHub2k datasets.
    if args.benchmarks:
        drain_parse(CONFIGS_2K)
        drain_benchmark(CONFIGS_2K)

    # Parsing Elfak datasets for downstream tasks (anomaly detection).
    if args.parsing:
        drain_parse(CONFIGS_ELFAK)


if __name__ == "__main__":
    main()
