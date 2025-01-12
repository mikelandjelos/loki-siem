import os
from io import TextIOWrapper
from typing import Any, Generator


def reversed_lines(file: TextIOWrapper) -> Generator[str, Any, None]:
    "Generate the lines of file in reverse order."
    part = ""
    for block in reversed_blocks(file):
        for c in reversed(block):
            if c == "\n" and part:
                yield part[::-1]
                part = ""
            part += c
    if part:
        yield part[::-1]


def reversed_blocks(file: TextIOWrapper, blocksize: int = 8192 * 2):
    "Generate blocks of file's contents in reverse order."
    file.seek(0, os.SEEK_END)
    here = file.tell()
    while 0 < here:
        delta = min(blocksize, here)
        here -= delta
        file.seek(here, os.SEEK_SET)
        yield file.read(delta)
