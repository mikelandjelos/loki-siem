from os import path

from pipelines.parsing.drain.configs.common import (
    COMMON_PATTERNS,
    RESULTS_ROOT_DIR,
    DrainConfig,
)

CONFIGS_NONLABELED = {
    "Apache Elfak": (
        DrainConfig(
            log_format=r"<ClientAddress> - - \[<Timestamp>\] \"<Content>\" <_StatusCode> <_ResponseBytes> \"<Referer>\" \"<UserAgent>\"",
            indir="data/24h/",
            outdir=path.join(RESULTS_ROOT_DIR, "drain/"),
            rex=COMMON_PATTERNS,
            st=0.4,
            depth=4,
        ),
        "Access Logs-data-2024-10-11 10_22_32.log",
    ),
}
