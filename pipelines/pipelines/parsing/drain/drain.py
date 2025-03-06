"""
Drain Log parser:
    - CLI argument parsing;
    - DRAIN log parsing;
    - DRAIN loghub2k datasets benchmarks;
    - DRAIN proprietary datasets parsing.
"""

import argparse
import logging
import os
from dataclasses import asdict
from time import perf_counter_ns
from typing import Optional

import pandas as pd
from logparser import Drain
from logparser.utils import evaluator

from .configs import (
    CONFIGS_2K,
    CONFIGS_ELFAK,
    OUTDIR_2K,
    OUTDIR_ELFAK,
    RESULTS_DIR,
    DrainConfig,
)
from .util import rename_files

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


def get_parser(parent_subparsers: Optional[argparse._SubParsersAction] = None):
    "Drain log parser."
    parser = (
        argparse.ArgumentParser(description=get_parser.__doc__)
        if not parent_subparsers
        else parent_subparsers.add_parser("drain", description=get_parser.__doc__)
    )
    parser.add_argument(
        "--loghub2k",
        action="store_true",
        help="Parse Loghub2k datasets, store results and output benchmarks.",
    )
    parser.add_argument(
        "--elfak", action="store_true", help="Parse Elfak datasets and store results."
    )
    parser.set_defaults(func=main)
    return parser


def main(args: Optional[argparse.Namespace] = None):
    __logger.setLevel(logging.INFO)

    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR, exist_ok=True)
        os.makedirs(OUTDIR_2K, exist_ok=True)
        os.makedirs(OUTDIR_ELFAK, exist_ok=True)

    if not args:
        args = get_parser().parse_args()

    # Benchmarking LogHub2k datasets.
    if args.loghub2k:
        drain_parse(CONFIGS_2K)
        drain_benchmark(CONFIGS_2K)

    # Parsing proprietary datasets.
    if args.elfak:
        drain_parse(CONFIGS_ELFAK)

    rename_files(RESULTS_DIR)


if __name__ == "__main__":
    main()
