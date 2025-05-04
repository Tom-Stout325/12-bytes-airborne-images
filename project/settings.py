from pathlib import Path
import os
import environ
import dj_database_url
from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured

# Load environment variables
env = environ.Env()
environ.Env.read_env()

# Validate required environment variables
required_env_vars = ['DJANGO_SECRET_KEY', 'ALLOWED_HOSTS', 'DATABASE_URL']
for var in required_env_vars:
    if not env(var, default=None):
        raise ImproperlyConfigured(f"Environment variable {var} is not set")

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Installed apps
INSTALLED_APPS = [
    'storages',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'whitenoise.runserver_nostatic',
    'app.apps.AppConfig',
    'drones.apps.DronesConfig',
    'finance',
    'crispy_forms',
    'crispy_bootstrap5',
    'bootstrap5',
    'fontawesomefree',
]

# Middleware
MIDDLEWARE = [
    'project.middleware.ForceHTTPSMiddleware',  # Enforce HTTPS
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URLs and WSGI
ROOT_URLCONF = 'project.urls'
WSGI_APPLICATION = 'project.wsgi.application'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=env("DATABASE_URL"),
        conn_max_age=600
    )
}

# Static and media files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
    if not DEBUG else
    'django.contrib.staticfiles.storage.StaticFilesStorage'
)

# S3 configuration
USE_S3 = env.bool("USE_S3", default=False)
if USE_S3:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default=None)
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default=None)
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default=None)
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-2')
    AWS_QUERYSTRING_AUTH = False
    AWS_DEFAULT_ACL = None
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Authentication
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'

# Session and CSRF settings
redis_url = env('REDISCLOUD_URL', default=env('REDIS_URL', default=None))
if redis_url:
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': redis_url,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 days
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_DOMAIN = '.airborne-images.net'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_DOMAIN = '.airborne-images.net'
CSRF_TRUSTED_ORIGINS = [
    'https://airborne-images-12bytes-5d4382c082a9.herokuapp.com',
    'https://*.herokuapp.com',
    'https://12bytes.airborne-images.net',
]

# Security headers
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Miscellaneous
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATE_INPUT_FORMATS = ['%d-%m-%Y']

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

# Jazzmin Admin UI
JAZZMIN_SETTINGS = {
    'site_title': 'App',
    'site_header': '/static/images/logo.png',
    'site_brand': 'App',
    'site_logo': '/static/images/logo.png',
    'login_logo': '/static/images/logo.png',
    'site_icon': '/static/images/logo.png',
    'login_logo_dark': '/static/images/logo.png',
    'copyright': '12bytes',
    'user_avatar': '/static/images/logo.png',
    'topmenu_links': [
        {'name': 'Admin Home', 'url': 'admin:index', 'permissions': ['auth.view_user']},
        {'name': 'auth.user'},
        {'name': 'Site Home', 'url': '/admin/logout', 'redirect': '/home/'},
    ],
}
JAZZMIN_UI_TWEAKS = {
    'theme': 'lux',
    'dark_mode_theme': 'darkly',
}

# Email settings
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.office365.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default=None)
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default=None)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='webmaster@localhost')