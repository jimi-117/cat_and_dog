import os
from datetime import datetime

# Settings to prepare the log files per month
current_time = datetime.now()
year_month = current_time.strftime("%Y/%m")

LOG_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", year_month)
os.makedirs(LOG_FOLDER, exist_ok=True)

def get_log_file_path(log_type: str) -> str:
    """Generate log file path based on log type and current date."""
    return os.path.join(LOG_FOLDER, f'{log_type}_{current_time.strftime("%Y-%m-%d")}.log')

ACCES_LOG = get_log_file_path('access')
ERROR_LOG = get_log_file_path('error')
APP_LOG = get_log_file_path('app')

# Settings for the loggings

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format' : '[%(asctime)s] %(levelname)-7s | %(name)s | %(funcName)s.%(lineno)d | %(message)s',
        },
        'app': {
            'format' : '[%(asctime)s] %(levelname)-7s | %(name)s | %(funcName)s.%(lineno)d | %(message)s',
        },
    },
    'handlers': {
        # Access log for werkzeug
        'access_log_handler' :{
            'level' : 'INFO',
            'class' : 'logging.handlers.TimedRotatingFileHandler',
            'filename': ACCES_LOG,
            'when' : 'midnight',
            'interval' : 1,
            'backupCount' : 7,
            'formatter': 'default',
        },
        # Error log
        'error_log_handler' :{
            'level' : 'ERROR',
            'class' : 'logging.handlers.TimedRotatingFileHandler',
            'filename': ERROR_LOG,
            'when' : 'midnight',
            'interval' : 1,
            'backupCount' : 7,
            'formatter': 'default',
        },
        # App log
        'app_log_handler' :{
            'level' : 'DEBUG',
            'class' : 'logging.handlers.TimedRotatingFileHandler',
            'filename': APP_LOG,
            'when' : 'midnight',
            'interval' : 1,
            'backupCount' : 7,
            'formatter': 'app',
        },
        # Console log for debugging
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers' : {
        # access log
        'access' : {
            'handlers': ['access_log_handler'],
            'level': 'INFO',
            'propagate': True,
        },
        # error log
        'error' : {
            'handlers': ['error_log_handler'],
            'level': 'ERROR',
            'propagate': True,
        },
        # app log
        'app' : {
            'handlers': ['app_log_handler'],
            'level': 'INFO',
            'propagate': True,
        },
        # console log
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}