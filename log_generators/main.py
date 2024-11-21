import argparse

from dotenv import find_dotenv, get_key, load_dotenv

from log_generators import GlobalConfig, parse_toml_config, start_generators

# TODO:
# - Correlation between streams.
# - SysLog handler, HTTP handler.
# - Different output formats - not just JSON formatted logs.
# - Different input formats - not just csv with header.
# - Documentation, dockerization, configs.


def main():
    config_path: str | None
    parser = argparse.ArgumentParser(prog="LogGenerator")
    parser.add_argument(
        "-c",
        "--config_path",
    )
    args = parser.parse_args()

    if args.config_path is not None:
        config_path = args.config_path
    else:
        assert (
            load_dotenv() is True
        ), "No CLI argument or .env (`CONFIG_PATH` key) given for configuration file path."
        config_path = get_key(find_dotenv(), "CONFIG_PATH")

    assert isinstance(
        config_path, str
    ), "Config file path not given! (can be given through .env or as a CLI argument)."

    generators_config: GlobalConfig = parse_toml_config(config_path)

    start_generators(generators_config.generator_configs)


if __name__ == "__main__":
    main()
