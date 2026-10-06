"""Service logger with configurable console and file handlers."""

from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Any

from app.core.config import get_settings

@dataclass(slots=True)
class LoggerConfig:
    """Configuration for :class:`ServiceLogger` handler and sink behavior."""

    service_name: str
    log_level: str = "INFO"
    log_to_console: bool = True
    log_to_file: bool = True
    log_file: str = "app.log"
    max_bytes: int = 10_000_000
    backup_count: int = 5
    logger_name: str = "app"

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

class FileLogFormatter(logging.Formatter):
    """Human-readable formatter."""

    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        super().__init__(
            fmt=(
                "%(asctime)s | "
                "%(levelname)-8s | "
                f"{service_name} | "
                "%(name)s | "
                "%(filename)s:%(lineno)d | "
                "%(message)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )

class ServiceLogger:
    """Service logger for application services."""

    def __init__(self, config: LoggerConfig) -> None:
        self.config = config

        self.logger = logging.getLogger(config.logger_name)
        self.logger.setLevel(
            LOG_LEVELS.get(config.log_level.upper(), logging.INFO)
        )
        self.logger.propagate = False

        self._ensure_handlers()

    def _ensure_handlers(self) -> None:
        """Attach handlers only once per logger."""

        if getattr(self.logger, "_shared_logger_initialized", False):
            return

        formatter = FileLogFormatter(service_name=self.config.service_name)

        if self.config.log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.logger.level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        if self.config.log_to_file:
            os.makedirs(
                os.path.dirname(self.config.log_file) or ".",
                exist_ok=True,
            )

            file_handler = RotatingFileHandler(
                filename=self.config.log_file,
                maxBytes=self.config.max_bytes,
                backupCount=self.config.backup_count,
                encoding="utf-8",
            )

            file_handler.setLevel(self.logger.level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.logger._shared_logger_initialized = True  # type: ignore[attr-defined]

    def log(
        self,
        level: int,
        message: str,
        *,
        extra: dict[str, Any] | None = None,
        exc_info: Any = None,
    ) -> None:
        """Log a message."""

        self.logger.log(
            level,
            message,
            extra=extra,
            exc_info=exc_info,
        )

    def debug(self, message: str, **kwargs: Any) -> None:
        self.log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self.log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self.log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self.log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self.log(logging.CRITICAL, message, **kwargs)

    def exception(
        self,
        message: str,
        *,
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Convenience method for logging exceptions."""
        self.logger.exception(message, extra=extra)

    def get_std_logger(self) -> logging.Logger:
        """Return the underlying Python logger."""
        return self.logger


@lru_cache(maxsize=1)
def get_logger() -> ServiceLogger:
    """Return the shared configured logger for the application."""
    settings = get_settings()
    config = LoggerConfig(
        service_name=settings.app_name,
        log_level=settings.log_level,
        log_to_console=True,
        log_to_file=True,
        log_file=str(
            Path(__file__).resolve().parents[2]
            / "logs"
            / f"{settings.app_name}.log"
        ),
    )
    return ServiceLogger(config)