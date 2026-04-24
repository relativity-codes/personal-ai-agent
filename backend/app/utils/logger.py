import logging
from typing import Any, Optional

def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger (``app.<module>`` style)."""
    return logging.getLogger(name)

log = logging.getLogger("app")

def log_exception(
    logger: logging.Logger, 
    e: Exception, 
    context: str = "Unhandled Exception",
    extra_data: Optional[Any] = None
):
    """
    General purpose exception logger that handles ExceptionGroups 
    and provides detailed diagnostic information.
    """
    logger.error(f"!!! {context} !!!")
    
    # Handle ExceptionGroups (Python 3.11+) to show all sub-exceptions
    if isinstance(e, BaseExceptionGroup):
        logger.error(f"ExceptionGroup detected with {len(e.exceptions)} exceptions:")
        for i, ex in enumerate(e.exceptions):
            logger.error(f"--- Sub-Exception {i+1} ---")
            logger.error(f"Type: {type(ex).__name__}")
            logger.error(f"Message: {str(ex)}")
    else:
        logger.error(f"Type: {type(e).__name__}")
        logger.error(f"Message: {str(e)}")
        
    logger.exception("Full stack trace:")
    
    if extra_data:
        logger.error(f"Context data: {extra_data}")
