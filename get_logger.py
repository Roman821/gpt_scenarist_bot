from logging import getLogger
from logging.config import dictConfig

from settings import Settings


dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'main': {
            'format': '[{levelname}] [{asctime}] path - "{pathname}" function - "{funcName}" message - "{message}"',
            'style': '{',
        },
        'short': {
            'format': '[{levelname}] [{asctime}] message - "{message}"',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'main',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'main',
            'filename': Settings.WARNING_LOG_FILE_PATH,
            'maxBytes': 1024 * 1024 * 10,  # 10 Mb
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'main': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
})


def get_logger(name):
    return getLogger(name)
