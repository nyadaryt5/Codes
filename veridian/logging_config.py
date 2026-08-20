from __future__ import annotations

import logging

LOG_FORMAT = "ts=%(asctime)s level=%(levelname)s logger=%(name)s msg=%(message)s"


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format=LOG_FORMAT, force=True)
