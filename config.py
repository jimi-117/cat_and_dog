import os
from datetime import datetime, timedelta, timezone

# Settings to prepare the log files per month

UTC_1 = timezone(timedelta(hours=1))
current_time_eu = datetime.now(UTC_1)
year_month = current_time_eu.strftime("%Y-%m")

LOG_FOLDER = os.path.join(os.path.dirname(__file__), "logs", year_month)
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

ACCES_LOG = os.path.join(LOG_FOLDER, f'access_{current_time_eu.strftime("%Y-%m-%d")}.log')
ERROR_LOG = os.path.join(LOG_FOLDER, f'error_{current_time_eu.strftime("%Y-%m-%d")}.log')
APP_LOG = os.path.join(LOG_FOLDER, f'app_{current_time_eu.strftime("%Y-%m-%d")}.log')

# Settings for the loggings

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format' : '[%(asctime)s] %(levelname)-7s | %(name)s | %(funcname)s.%(lineno)d | %(message)s',
        },
        'app': {
            'format' : '[%(asctime)s] %(levelname)-7s | %(name)s | %(funcname)s.%(lineno)d | %(message)s',
        },
    },
    'handlers': {
        # Access log for werkzeug
        'access_log_handler' :{
            'level' : 'INFO',
            'class' : 'logging.handlers.TimeRotatingFileHandler',
            'filename': ACCES_LOG,
            'when' : 'midnight',
            'interval' : 1,
            'buckupCount' : 7,
            'formatter': 'default',
        },
        # Error log
        'error_log_handler' :{
            'level' : 'ERROR',
            'class' : 'logging.handlers.TimeRotatingFileHandler',
            'filename': ERROR_LOG,
            'when' : 'midnight',
            'interval' : 1,
            'buckupCount' : 7,
            'formatter': 'default',
        },
        # App log
        'app_log_handler' :{
            'level' : 'DEBUG',
            'class' : 'logging.handlers.TimeRotatingFileHandler',
            'filename': APP_LOG,
            'when' : 'midnight',
            'interval' : 1,
            'buckupCount' : 7,
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