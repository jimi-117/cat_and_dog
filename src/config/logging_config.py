import os
from datetime import datetime

# log file path
current_time = datetime.now()
year_month = current_time.strftime("%Y/%m")

def get_log_folder():
    log_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                             "data", "logs", year_month)
    os.makedirs(log_folder, exist_ok=True)
    return log_folder

def get_log_file_path(log_type: str) -> str:
    """Generate log file path based on log type and current date."""
    log_folder = get_log_folder()
    return os.path.join(log_folder, f'{log_type}_{current_time.strftime("%Y-%m-%d")}.log')

ACCESS_LOG = get_log_file_path('access')
ERROR_LOG = get_log_file_path('error')
APP_LOG = get_log_file_path('app')

# conf logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)-7s | %(name)s | %(funcName)s.%(lineno)d | %(message)s',
        },
        'app': {
            'format': '[%(asctime)s] %(levelname)-7s | %(name)s | %(funcName)s.%(lineno)d | %(message)s',
        },
    },
    'handlers': {
        'access_log_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': ACCESS_LOG,
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'formatter': 'default',
        },
        'error_log_handler': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': ERROR_LOG,
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'formatter': 'default',
        },
        'app_log_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': APP_LOG,
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'formatter': 'app',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        'access': {
            'handlers': ['access_log_handler'],
            'level': 'INFO',
            'propagate': True,
        },
        'error': {
            'handlers': ['error_log_handler'],
            'level': 'ERROR',
            'propagate': True,
        },
        'app': {
            'handlers': ['app_log_handler'],
            'level': 'INFO',
            'propagate': True,
        },
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}