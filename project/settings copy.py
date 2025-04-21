from pathlib import Path
import os
import environ
import secrets
from django.conf import settings
import dj_database_url



env = environ.Env()

environ.Env.read_env()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    default=secrets.token_urlsafe(nbytes=64),
)

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = []
    
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
    "whitenoise.runserver_nostatic",

    'app.apps.AppConfig',
    'drone.apps.DroneConfig',

    'finance',
    "crispy_forms",
    "crispy_bootstrap5",
    'bootstrap5',
    'fontawesomefree',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "templates",
            ],
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

WSGI_APPLICATION = 'project.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-   C U S T O M   S E T T I N G S  _-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_#

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}


#Email Setup
EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")


# Database
DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE'),
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env.int("DB_PORT", default=5432),
    }
}
#Defalut database if PostgreSQL has not been set up yet:
DATABASES = {
    'default': env.db(default=f'sqlite:///' + str(BASE_DIR / 'db.sqlite3'))
}



USE_S3 = env.bool("USE_S3", default=False)

if USE_S3:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_QUERYSTRING_AUTH = False
    AWS_DEFAULT_ACL = None
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

print("USE_S3 =", USE_S3)
print("DEFAULT_FILE_STORAGE =", DEFAULT_FILE_STORAGE if USE_S3 else "django.core.files.storage.FileSystemStorage")


AWS_QUERYSTRING_AUTH = False  # Set to True for private URLs
AWS_DEFAULT_ACL = None

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

# Used for Custom User Model:
#AUTH_USER_MODEL = 'account.Account'

WHITENOISE_USE_FINDERS = True

DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760    #-----limits file size for uploads

DATE_INPUT_FORMATS = ['%d-%m-%Y']  # --------------------------- Date format

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LLOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'

JAZZMIN_SETTINGS = {
    'site_title': "App",
    'site_header': "images/logo.png",
    'site_brand': 'App',
    'site_logo': "images/logo.png",
    'login_logo': "images/logo.png",
    'site_icon': "images/logo.png",
    'login_logo_dark': "images/logo.png",
    "copyright": "12bytes",
    "user_avatar": "images/logo.png",

    "topmenu_links": [
        {"name": "Admin Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "auth.user"},
        {"name": "Site Home", "url": "/admin/logout", "redirect": "/home/"}
    ]
}

# Select your Jazzmin theme here:  https://django-jazzmin.readthedocs.io/ui_customisation/
JAZZMIN_UI_TWEAKS = {
    "theme": "lux",
    "dark_mode_theme": "darkly",
}

#=-=-=-=-=-=-=-=-=-=-=-=-=->  PRODUCTION SETTINGS:  Remove all # below

# Email settings (fallback to console backend)
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# Static files storage
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
