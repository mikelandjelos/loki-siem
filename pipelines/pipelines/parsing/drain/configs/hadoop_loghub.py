from os import path

from .common import COMMON_PATTERNS, RESULTS_ROOT_DIR, DrainConfig

HADOOP_LOGHUB: DrainConfig = DrainConfig(
    log_format=r"<Year>-<Month>-<Day> <Time> <LogLevel> \[<Thread>\] <Logger>\: <Content>",
    indir="data/loghub_full/Hadoop",
    outdir=path.join(RESULTS_ROOT_DIR, "drain/"),
    rex=COMMON_PATTERNS,
    st=0.4,  # Similarity threshold - greater ST, greater number of templates
    depth=4,  # Depth of the tree - greater depth, greater number of templates
)
