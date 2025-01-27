from dataclasses import dataclass, field


@dataclass
class DrainConfig:
    log_format: str
    indir: str = "./"
    outdir: str = "./result/"
    depth: int = 4
    st: float = 0.4
    maxChild: int = 100
    rex: list[str] = field(default_factory=list)
    keep_para: bool = True


COMMON_PATTERNS = [  # Common patterns found in logs
    r"(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)",  # IPv4
    r"^(https?://)?([a-zA-Z0-9.-]+)(:[0-9]+)?(/.*)?$",  # URL
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",  # Email
    r"[1-5][0-9]{2}",  # Http Status codes
]

RESULTS_ROOT_DIR = "results"
