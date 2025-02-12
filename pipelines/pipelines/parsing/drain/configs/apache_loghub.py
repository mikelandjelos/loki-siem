from os import path

from .common import COMMON_PATTERNS, RESULTS_ROOT_DIR, DrainConfig

APACHE_LOGHUB: DrainConfig = DrainConfig(
    log_format=r"\[<Weekday> <Month> <Day> <Time> <Year>\] \[<Level>\] <Content>",
    indir="data/loghub_full/Apache",
    outdir=path.join(RESULTS_ROOT_DIR, "drain/"),
    rex=COMMON_PATTERNS,
    st=0.4,  # Similarity threshold - greater ST, greater number of templates
    depth=4,  # Depth of the tree - greater depth, greater number of templates
)
