from os import mkdir, path

from .common import COMMON_PATTERNS, RESULTS_ROOT_DIR, DrainConfig

APACHE_ELFAK_CONFIG: DrainConfig = DrainConfig(
    # Content = RequestHeader + ResponseStatusCode + ResponseSizeInBytes
    # log_format=r"<ClientAddress> - - \[<Timestamp>\] \"<Method> <Content> <ProtocolVersion>\" <_StatusCode> <_ResponseBytes> \"<Referer>\" \"<UserAgent>\"",
    log_format=r"<ClientAddress> - - \[<Timestamp>\] \"<Content>\" <_StatusCode> <_ResponseBytes> \"<Referer>\" \"<UserAgent>\"",
    # log_format=r"<ClientAddress> - - \[<Timestamp>\] \"<Content> \"<Referer>\" \"<UserAgent>\"",
    indir="data/24h/",
    outdir=path.join(RESULTS_ROOT_DIR, "drain/"),
    rex=COMMON_PATTERNS,
    st=0.4,
    depth=4,
)
