import sys
from logging import FileHandler, Handler, StreamHandler
from logging.handlers import DatagramHandler, HTTPHandler, SocketHandler
from typing import Any, Literal, Type

import validators
from pydantic import BaseModel, model_validator

LogOutputType = Literal[
    "STREAM",
    "FILE",
    "TCP",
    "UDP",
    "HTTP",
]

LOGGING_HANDLERS: dict[LogOutputType, Type[Handler]] = {
    "STREAM": StreamHandler,
    "FILE": FileHandler,
    "TCP": SocketHandler,
    "UDP": DatagramHandler,
    "HTTP": HTTPHandler,
}


class LogOutput(BaseModel):
    type: LogOutputType
    arguments: dict[str, Any]

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data: dict[str, Any]) -> dict[str, Any]:
        handler_type = data["type"]
        handler_arguments = data["arguments"]

        assert (
            handler_type == "STREAM"
            or handler_type == "FILE"
            or handler_type == "TCP"
            or handler_type == "UDP"
            or handler_type == "HTTP"
        ), f"Handler type `{handler_type}` is of type {type(handler_type)}"

        match handler_type:
            case "STREAM":
                stream_label = handler_arguments.get("stream", None)
                assert (
                    stream_label is not None
                ), f"Standard stream name must be provided (`stderr`, `stdout`)."
                assert isinstance(
                    stream_label, str
                ), f"Stream label must be a string. Instead it's `{type(stream_label)}`."
                stream_label = stream_label.lower()
                assert (
                    stream_label == "stderr" or stream_label == "stdout"
                ), "Stream must be `stdout` or `stderr`"
                handler_arguments["stream"] = {
                    "stderr": sys.stderr,
                    "stdout": sys.stdout,
                }.get(stream_label)
            case "FILE":
                assert "filename" in handler_arguments, "Filename must be provided"
                assert isinstance(
                    handler_arguments["filename"], str
                ), "Filename must be a string."
            case "TCP" | "UDP":
                assert "port" in handler_arguments, "Port must be provided."
                assert isinstance(
                    handler_arguments["port"], int
                ), f"Port must be an integer. Instead it's {type(handler_arguments["port"])}"
                assert "host" in handler_arguments, f"Host must be provided."
                assert isinstance(
                    handler_arguments["host"], str
                ), f"Host must be a string. Instead it's {type(handler_arguments["host"])}"
            case "HTTP":
                assert "host" in handler_arguments, "Host must be provided."
                assert "url" in handler_arguments, "URL must be provided."
                assert isinstance(
                    handler_arguments["host"], str
                ), f"Host must be a string. Instead it's {type(handler_arguments["host"])}"
                assert isinstance(
                    handler_arguments["url"], str
                ), f"URL must be a string. Instead it's {type(handler_arguments["url"])}"
                assert validators.url(
                    handler_arguments["url"]
                ), "Given URL must be valid."
                assert (
                    handler_arguments.get("method") is None
                    or handler_arguments["method"] == "GET"
                    or handler_arguments["method"] == "POST"
                ), f"Method must be `GET` or `POST`. Instead it's {handler_arguments["method"]}"
                raise NotImplementedError  # TODO: Not supported yet!

        return data
