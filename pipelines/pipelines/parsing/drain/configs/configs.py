from .apache_2k_config import APACHE_2K_CONFIG
from .apache_elfak_config import APACHE_ELFAK_CONFIG

# <semantic_name>: (<config_object>, <log_file>)

CONFIGS = {
    "apache_2k": (APACHE_2K_CONFIG, "Apache_2k.log"),
    "apache_elfak": (APACHE_ELFAK_CONFIG, "Access Logs-data-2024-10-11 10_22_32.log"),
}
