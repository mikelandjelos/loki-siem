from logging import FileHandler, Handler, LogRecord, StreamHandler
from logging.handlers import DatagramHandler, HTTPHandler, SocketHandler
from typing import Literal, Type


class TCPRawHandler(SocketHandler):
    def makePickle(self, record: LogRecord):
        return (record.getMessage() + "\n").encode()


class UDPRawHandler(DatagramHandler):
    def makePickle(self, record: LogRecord):
        return (record.getMessage() + "\n").encode()


# Difference between raw and regular:
# - Regular pickle the complete LogRecord when sending over a socket.
# - Raw just send raw bytes of a log.

LOGGING_HANDLERS: dict[
    Literal["STREAM", "FILE", "TCP_RAW", "TCP", "UDP_RAW", "UDP", "HTTP"],
    Type[Handler],
] = {
    "STREAM": StreamHandler,
    "FILE": FileHandler,
    "TCP_RAW": TCPRawHandler,
    "TCP": SocketHandler,
    "UDP_RAW": UDPRawHandler,
    "UDP": DatagramHandler,
    "HTTP": HTTPHandler,
}
