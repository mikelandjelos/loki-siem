from .apache_elfak_config import APACHE_ELFAK_CONFIG
from .apache_loghub import APACHE_LOGHUB
from .hadoop_loghub import HADOOP_LOGHUB
from .openssh_loghub import OPENSSH_LOGHUB

# <semantic_name>: (<config_object>, <log_file>)

CONFIGS = {
    # "apache_loghub": (APACHE_LOGHUB, "Apache_full.log"),
    # "openssh_loghub": (OPENSSH_LOGHUB, "OpenSSH_full.log"),
    "hadoop_loghub": (HADOOP_LOGHUB, "Hadoop_full.log"),
    # "apache_elfak": (APACHE_ELFAK_CONFIG, "Access Logs-data-2024-10-11 10_22_32.log"),
}
