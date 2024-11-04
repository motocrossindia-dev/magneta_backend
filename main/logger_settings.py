
base_location = r'logs/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': r'logs/debug.log',
            'formatter': 'standard',
        },
        'magneta_handler': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': r'logs/magneta_debug.log',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'magneta_logger': {
            'handlers': ['console', 'magneta_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
