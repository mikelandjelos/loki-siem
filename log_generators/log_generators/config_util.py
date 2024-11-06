import logging

from dotenv import dotenv_values, find_dotenv, load_dotenv

logger = logging.getLogger(__file__)


def bootstrap_dotenv():
    dotenv_path = find_dotenv(
        raise_error_if_not_found=True,
        usecwd=True,
    )

    if not load_dotenv(dotenv_path):
        raise EnvironmentError("No environment variables set!")

    for key, value in dotenv_values().items():
        logger.info(f"{key}=`{value}`")


__all__ = [
    "bootstrap_dotenv",
]
