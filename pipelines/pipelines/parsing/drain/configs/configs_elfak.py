from os import path

from pipelines.parsing.drain.configs.common import (
    COMMON_PATTERNS,
    RESULTS_DIR,
    DrainConfig,
)

OUTDIR_ELFAK = path.join(RESULTS_DIR, "elfak")
INDIR_ELFAK = path.join("data", "elfak")

CONFIGS_ELFAK = {
    "Apache": (
        DrainConfig(
            log_format=r"<ClientAddress> - - \[<Timestamp>\] \"<Content>\" <StatusCode> <ResponseBytes> \"<Referer>\" \"<UserAgent>\"",
            indir=path.join(INDIR_ELFAK, "24h"),
            outdir=OUTDIR_ELFAK,
            rex=COMMON_PATTERNS,
            st=0.4,
            depth=4,
        ),
        "Access Logs-data-2024-10-11 10_22_32.log",
    ),
}
