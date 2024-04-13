import logging
from typing import Optional
import colorama
from termcolor import colored
from pathlib import Path
import sys
import time
import os
from typing import Self, Union

__LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class SaneLogging:
    def __init__(self) -> None:
        self.__file_level: Optional[str] = None
        self.__terminal_level: Optional[str] = None
        self.__file_directory: Optional[Path] = None
        self.__clean_directory: bool = False

    def terminal(self, level: str = "INFO") -> Self:
        assert level in __LEVELS
        self.__terminal_level = level
        return self

    def file(self, directory: Union[str, os.PathLike], level: str = "DEBUG", clean: bool = False) -> Self:
        assert level in __LEVELS
        self.__file_directory = Path(directory)
        self.__file_level = level
        self.__clean_directory = clean
        return self

    def apply(self, logger: logging.Logger) -> None:
        if self.__terminal_level is not None:
            terminal_handler = logging.StreamHandler(stream=sys.stdout)
            terminal_handler.setLevel(self.__terminal_level)
            terminal_handler.setFormatter(_ColoredFormatter())
            logger.addHandler(terminal_handler)

        if self.__file_level is not None and self.__file_directory is not None:
            self.__file_directory.mkdir(exist_ok=True, parents=True)
            if self.__clean_directory:
                for old in self.__file_directory.iterdir():
                    try:
                        old.unlink()
                    except OSError as error:
                        logger.error("Failed to remove old log file: %s", str(error))

            file_formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)s]: %(message)s")

            file_handler = logging.FileHandler(self.__file_directory / time.strftime("%Y_%m_%d-%H_%M_%S.log"))
            file_handler.setLevel(self.__file_level)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)


class _ColoredFormatter(logging.Formatter):
    TEXT = "[%(levelname)s] %(module)s: %(message)s"
    FORMATERS = {
        logging.DEBUG: logging.Formatter(colored(TEXT, "light_grey")),
        logging.INFO: logging.Formatter(colored(TEXT, "blue")),
        logging.WARNING: logging.Formatter(colored(TEXT, "yellow", attrs=["bold"])),
        logging.ERROR: logging.Formatter(colored(TEXT, "red", attrs=["bold"])),
        logging.CRITICAL: logging.Formatter(colored(TEXT, "red", attrs=["bold", "underline"])),
    }

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        colorama.just_fix_windows_console()
        super(_ColoredFormatter, self).__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        if record.levelno in self.FORMATERS:
            return self.FORMATERS[record.levelno].format(record)
        return f"Error log formating, formater for {record.levelno} not found"
