"""
Django settings for recipesnstuff project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# required environment variables are keys of 'scheme' plus REQUIRED_ENV_VARS
scheme = {
    # set casting, default value
    'DEBUG': (bool, False),
    'DEVELOPMENT': (bool, False),
    'TEST': (bool, False),
}
REQUIRED_ENV_VARS = [key for key, _ in scheme.items()]
REQUIRED_ENV_VARS.extend(['SITE_ID', 'SECRET_KEY', 'DATABASE_URL'])

env = environ.Env(**scheme)
# Take environment variables from .env file
os.environ.setdefault('ENV_FILE', '.env')
environ.Env.read_env(
    os.path.join(BASE_DIR, env('ENV_FILE'))
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')
DEVELOPMENT = env('DEVELOPMENT')
TEST = env('TEST')

if env('DEVELOPMENT'):
    ALLOWED_HOSTS = ['testserver'] \
        if env('TEST') else ['localhost', '127.0.0.1']
else:
    ALLOWED_HOSTS = env.list('HEROKU_HOSTNAME')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',

    # https://pypi.org/project/dj3-cloudinary-storage/
    # If using for static and/or media files, make sure that cloudinary_storage
    # is before django.contrib.staticfiles
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'recipesnstuff.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'recipesnstuff.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    # read os.environ['DATABASE_URL'] and raises
    # ImproperlyConfigured exception if not found
    #
    # The db() method is an alias for db_url().
    'default': env.db(),

    # read os.environ['REMOTE_DATABASE_URL']
    'remote': env.db_url(
        'REMOTE_DATABASE_URL',
        default=f'sqlite:///{os.path.join(BASE_DIR, "temp-remote.sqlite3")}'
    ),

    # read os.environ['SQLITE_URL']
    'extra': env.db_url(
        'SQLITE_URL',
        default=f'sqlite:///{os.path.join(BASE_DIR, "temp-sqlite.sqlite3")}'
    )
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [{
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    }, {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    }, {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

# !!
# https://github.com/klis87/django-cloudinary-storage
# Please note that you must set DEBUG to False to fetch static files from
# Cloudinary.
# With DEBUG equal to True, Django staticfiles app will use your local files
# for easier and faster development
# (unless you use cloudinary_static template tag).
# !!

# URL to use when referring to static files located in STATIC_ROOT
STATIC_URL = 'static/'
# https://docs.djangoproject.com/en/4.1/ref/settings/#staticfiles-storage
STATICFILES_STORAGE = \
    'django.contrib.staticfiles.storage.StaticFilesStorage' \
    if DEVELOPMENT else \
    'cloudinary_storage.storage.StaticHashedCloudinaryStorage'
# https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-STATICFILES_DIRS
# Additional locations the staticfiles app will traverse for collectstatic
STATICFILES_DIRS = [
    # directories that will be found by staticfiles’s finders are by default,
    # are 'static/' app sub-directories and any directories included in
    # STATICFILES_DIRS
    os.path.join(BASE_DIR, 'static')
]
# absolute path to the directory where static files are collected for
# deployment
# https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-STATIC_ROOT
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = 'media/'
# https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-MEDIA_ROOT
MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_URL)

# https://docs.djangoproject.com/en/4.1/ref/settings/#default-file-storage
DEFAULT_FILE_STORAGE = \
    'django.core.files.storage.FileSystemStorage' \
    if DEVELOPMENT else \
    'cloudinary_storage.storage.MediaCloudinaryStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
