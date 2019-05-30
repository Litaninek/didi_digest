from .base import *

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    'debug_toolbar',
    # CORS
    'corsheaders',
]

MIDDLEWARE.insert(2, 'corsheaders.middleware.CorsMiddleware')

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# debug_toolbar IPS
INTERNAL_IPS = ['127.0.0.1']

# CORS
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (
    'localhost:4200',
)

CORS_ORIGIN_REGEX_WHITELIST = (
    'localhost:4200',
)
