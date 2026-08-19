import logging
import structlog


def get_logger(name: str):
    try:
        from neuroforge.config import config

        log_level_str = config.LOG_LEVEL
    except Exception:
        log_level_str = "INFO"

    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
    return structlog.get_logger(name)
