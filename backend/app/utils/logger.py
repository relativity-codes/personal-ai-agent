import logging


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger (``app.<module>`` style)."""
    return logging.getLogger(name)


log = logging.getLogger("app")
