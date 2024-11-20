from logging import FATAL, log

from dotenv import find_dotenv, get_key, load_dotenv

from log_generators import GlobalConfig, parse_toml_config, start_generators

# TODO:
# - SysLog handler, HTTP handler.
# - Different output formats - not just JSON formatted logs.
# - Different input formats - not just csv with header.
# - Documentation, dockerization, configs.


def main():
    load_dotenv()
    config_path = get_key(find_dotenv(), "CONFIG_PATH")

    if config_path is None:
        msg = "Config path (`CONFIG_PATH` environment variable) not provided!"
        log(FATAL, msg)
        raise EnvironmentError(msg)

    generators_config: GlobalConfig = parse_toml_config(config_path)

    start_generators(generators_config.generator_configs)


if __name__ == "__main__":
    main()
