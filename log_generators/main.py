from log_generators import GlobalConfig, parse_toml_config, start_generators


def main():
    config_path = "./configs/test_config.toml"
    generators_config: GlobalConfig = parse_toml_config(config_path)

    start_generators(generators_config.generator_configs)


if __name__ == "__main__":
    main()
