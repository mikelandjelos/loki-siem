from os import path

from .common import RESULTS_ROOT_DIR, DrainConfig

OUTDIR_2K = path.join(RESULTS_ROOT_DIR, "loghub_2k")
INDIR_2K = path.join("data", "loghub_2k")

# <semantic_name>: (<config_object>, <log_file>)

CONFIGS_2K = {
    "HDFS": (
        DrainConfig(
            log_format=r"<Date> <Time> <Pid> <Level> <Component>: <Content>",
            indir=path.join(INDIR_2K, "HDFS"),
            outdir=OUTDIR_2K,
            rex=[
                r"blk_-?\d+",
                r"(\d+\.){3}\d+(:\d+)?",
            ],
            st=0.5,
            depth=4,
        ),
        "HDFS_2k.log",
    ),
    "Hadoop": (
        DrainConfig(
            log_format=r"<Date> <Time> <Level> \[<Process>\] <Component>: <Content>",
            indir=path.join(INDIR_2K, "Hadoop"),
            outdir=OUTDIR_2K,
            rex=[
                r"(\d+\.){3}\d+",
            ],
            st=0.5,
            depth=4,
        ),
        "Hadoop_2k.log",
    ),
    "Spark": (
        DrainConfig(
            log_format=r"<Date> <Time> <Level> <Component>: <Content>",
            indir=path.join(INDIR_2K, "Spark"),
            outdir=OUTDIR_2K,
            rex=[
                r"(\d+\.){3}\d+",
                r"\b[KGTM]?B\b",
                r"([\w-]+\.){2,}[\w-]+",
            ],
            st=0.5,
            depth=4,
        ),
        "Spark_2k.log",
    ),
    "Zookeeper": (
        DrainConfig(
            log_format=r"<Date> <Time> - <Level>  \[<Node>:<Component>@<Id>\] - <Content>",
            indir=path.join(INDIR_2K, "Zookeeper"),
            outdir=OUTDIR_2K,
            rex=[
                r"(/|)(\d+\.){3}\d+(:\d+)?",
            ],
            st=0.5,
            depth=4,
        ),
        "Zookeeper_2k.log",
    ),
    "BGL": (
        DrainConfig(
            log_format=r"<Label> <Timestamp> <Date> <Node> <Time> <NodeRepeat> <Type> <Component> <Level> <Content>",
            indir=path.join(INDIR_2K, "BGL"),
            outdir=OUTDIR_2K,
            rex=[
                r"core\.\d+",
            ],
            st=0.5,
            depth=4,
        ),
        "BGL_2k.log",
    ),
    "HPC": (
        DrainConfig(
            log_format=r"<LogId> <Node> <Component> <State> <Time> <Flag> <Content>",
            indir=path.join(INDIR_2K, "HPC"),
            outdir=OUTDIR_2K,
            rex=[
                r"=\d+",
            ],
            st=0.5,
            depth=4,
        ),
        "HPC_2k.log",
    ),
    "Thunderbird": (
        DrainConfig(
            log_format=r"<Label> <Timestamp> <Date> <User> <Month> <Day> <Time> <Location> <Component>(\[<PID>\])?: <Content>",
            indir=path.join(INDIR_2K, "Thunderbird"),
            outdir=OUTDIR_2K,
            rex=[
                r"(\d+\.){3}\d+",
            ],
            st=0.5,
            depth=4,
        ),
        "Thunderbird_2k.log",
    ),
    "Windows": (
        DrainConfig(
            log_format=r"<Date> <Time>, <Level>                  <Component>    <Content>",
            indir=path.join(INDIR_2K, "Windows"),
            outdir=OUTDIR_2K,
            rex=[
                r"0x.*?\s",
            ],
            st=0.7,
            depth=5,
        ),
        "Windows_2k.log",
    ),
    "Linux": (
        DrainConfig(
            log_format=r"<Month> <Date> <Time> <Level> <Component>(\[<PID>\])?: <Content>",
            indir=path.join(INDIR_2K, "Linux"),
            outdir=OUTDIR_2K,
            rex=[
                r"(\d+\.){3}\d+",
                r"\d{2}:\d{2}:\d{2}",
            ],
            st=0.39,
            depth=6,
        ),
        "Linux_2k.log",
    ),
    "Android": (
        DrainConfig(
            log_format=r"<Date> <Time>  <Pid>  <Tid> <Level> <Component>: <Content>",
            indir=path.join(INDIR_2K, "Android"),
            outdir=OUTDIR_2K,
            rex=[
                r"(/[\w-]+)+",
                r"([\w-]+\.){2,}[\w-]+",
                r"\b(\-?\+?\d+)\b|\b0[Xx][a-fA-F\d]+\b|\b[a-fA-F\d]{4,}\b",
            ],
            st=0.2,
            depth=6,
        ),
        "Android_2k.log",
    ),
    "HealthApp": (
        DrainConfig(
            log_format=r"<Time>\|<Component>\|<Pid>\|<Content>",
            indir=path.join(INDIR_2K, "HealthApp"),
            outdir=OUTDIR_2K,
            rex=[],
            st=0.2,
            depth=4,
        ),
        "HealthApp_2k.log",
    ),
    "Apache": (
        DrainConfig(
            log_format=r"\[<Time>\] \[<Level>\] <Content>",
            indir=path.join(INDIR_2K, "Apache"),
            outdir=OUTDIR_2K,
            rex=[
                r"(\d+\.){3}\d+",
            ],
            st=0.5,
            depth=4,
        ),
        "Apache_2k.log",
    ),
    "Proxifier": (
        DrainConfig(
            log_format=r"\[<Time>\] <Program> - <Content>",
            indir=path.join(INDIR_2K, "Proxifier"),
            outdir=OUTDIR_2K,
            rex=[
                r"<\d+\ssec",
                r"([\w-]+\.)+[\w-]+(:\d+)?",
                r"\d{2}:\d{2}(:\d{2})*",
                r"[KGTM]B",
            ],
            st=0.6,
            depth=3,
        ),
        "Proxifier_2k.log",
    ),
    "OpenSSH": (
        DrainConfig(
            log_format=r"<Date> <Day> <Time> <Component> sshd\[<Pid>\]\: <Content>",
            indir=path.join(INDIR_2K, "OpenSSH"),
            outdir=OUTDIR_2K,
            rex=[
                r"(\d+\.){3}\d+",
                r"([\w-]+\.){2,}[\w-]+",
            ],
            st=0.6,
            depth=5,
        ),
        "OpenSSH_2k.log",
    ),
    "OpenStack": (
        DrainConfig(
            log_format=r"<Logrecord> <Date> <Time> <Pid> <Level> <Component> \[<ADDR>\] <Content>",
            indir=path.join(INDIR_2K, "OpenStack"),
            outdir=OUTDIR_2K,
            rex=[
                r"((\d+\.){3}\d+,?)+",
                r"/.+?\s",
                r"\d+",
            ],
            st=0.5,
            depth=5,
        ),
        "OpenStack_2k.log",
    ),
    "Mac": (
        DrainConfig(
            log_format=r"<Month>  <Date> <Time> <User> <Component>\[<PID>\]( \(<Address>\))?: <Content>",
            indir=path.join(INDIR_2K, "Mac"),
            outdir=OUTDIR_2K,
            rex=[
                r"([\w-]+\.){2,}[\w-]+",
            ],
            st=0.7,
            depth=6,
        ),
        "Mac_2k.log",
    ),
}
