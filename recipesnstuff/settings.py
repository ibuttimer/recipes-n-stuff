#  MIT License
#
#  Copyright (c) 2023 Ian Buttimer
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM,OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

"""
Django settings for recipesnstuff project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

import environ
from django.contrib.messages import constants as messages

from recipes.constants import RECIPE_HOME_ROUTE_NAME
from .constants import (
    BASE_APP_NAME, MIN_PASSWORD_LEN, USER_APP_NAME, PROFILES_APP_NAME,
    RECIPES_APP_NAME, SUBSCRIPTION_APP_NAME, CHECKOUT_APP_NAME,
    LOGIN_URL as USER_LOGIN_URL, LOGIN_ROUTE_NAME, HOME_ROUTE_NAME,
    ORDER_APP_NAME
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# name of main app
MAIN_APP = Path(__file__).resolve().parent.name

# required environment variables are keys of 'scheme' plus REQUIRED_ENV_VARS
scheme = {
    # set casting, default value
    'DEBUG': (bool, False),
    'DEVELOPMENT': (bool, False),
    'TEST': (bool, False),
    'DEFAULT_SEND_EMAIL': (str, ''),
    'EMAIL_HOST': (str, ''),
    'EMAIL_USE_TLS': (bool, True),
    'EMAIL_PORT': (int, 587),
    'EMAIL_HOST_USER': (str, ''),
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
DBG_TOOLBAR = env('DBG_TOOLBAR', default=False) and DEBUG

# https://docs.djangoproject.com/en/4.1/ref/clickjacking/
# required for Summernote editor
X_FRAME_OPTIONS = 'SAMEORIGIN'
SUMMERNOTE_THEME = 'bs4'    # TODO bs5 not working at the moment
# https://github.com/summernote/django-summernote#options
SUMMERNOTE_CONFIG = {
    # Using SummernoteWidget - iframe mode, default
    'iframe': True,

    # You can put custom Summernote settings
    'summernote': {
        # As an example, using Summernote Air-mode
        'airMode': False,

        # Change editor size
        'width': '100%',
        'height': '480',

        # Use proper language setting automatically (default)
        'lang': None,

        # Toolbar customization
        # https://summernote.org/deep-dive/#custom-toolbar-popover
        'toolbar': [
            ['style', ['style']],
            ['font', ['bold', 'underline', 'clear']],
            ['fontname', ['fontname']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['insert', ['link', 'picture']],
            ['view', ['fullscreen', 'codeview', 'help']],
        ],
    },
    # Require users to be authenticated for uploading attachments.
    'attachment_require_authentication': True,

    # Lazy initialization
    # If you want to initialize summernote at the bottom of page,
    # set this as True and call `initSummernote()` on your page.
    'lazy': False,
    # TODO need to figure out initSummernote for admin site to enable this
}

if env('DEVELOPMENT'):
    ALLOWED_HOSTS = ['testserver'] \
        if env('TEST') else ['localhost', '127.0.0.1']
else:
    ALLOWED_HOSTS = env.list('HEROKU_HOSTNAME')

INTERNAL_IPS = [
    "127.0.0.1",
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',

    # The following apps are required by 'allauth':
    #   django.contrib.auth, django.contrib.messages
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',

    # https://pypi.org/project/dj3-cloudinary-storage/
    # If using for static and/or media files, make sure that cloudinary_storage
    # is before django.contrib.staticfiles
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    'django_summernote',

    'django_countries',

    BASE_APP_NAME,
    USER_APP_NAME,
    PROFILES_APP_NAME,
    RECIPES_APP_NAME,
    SUBSCRIPTION_APP_NAME,
    CHECKOUT_APP_NAME,
    ORDER_APP_NAME,

    # needs to be after app with django template overrides
    'django.forms',
]
if DBG_TOOLBAR:
    INSTALLED_APPS.append("debug_toolbar")

# To supply custom templates to django widgets:
# 1) Add 'django.forms' to INSTALLED_APPS; *after* the app with the overrides.
# 2) Add FORM_RENDERER = 'django.forms.renderers.TemplatesSetting' to
#    settings.py.
# Courtesy of https://stackoverflow.com/a/52184422/4054609
# https://docs.djangoproject.com/en/4.1/ref/forms/renderers/#django.forms.renderers.TemplatesSetting
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware"
] if DBG_TOOLBAR else []
MIDDLEWARE.extend([
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    f'{SUBSCRIPTION_APP_NAME}.middleware.SubscriptionMiddleware',
])

# https://docs.djangoproject.com/en/4.1/ref/settings/#root-urlconf
ROOT_URLCONF = f'{MAIN_APP}.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # `allauth` needs this from django
                'django.template.context_processors.request',

                # app-specific context processors
                f'{MAIN_APP}.context_processors.footer_context',
                f'{BASE_APP_NAME}.context_processors.base_context',
                f'{CHECKOUT_APP_NAME}.context_processors.checkout_context',
                f'{USER_APP_NAME}.context_processors.user_context',
                f'{SUBSCRIPTION_APP_NAME}.context_processors'
                f'.subscription_context',
                f'{RECIPES_APP_NAME}.context_processors.recipe_context',
            ],
        },
    },
]

# email
if DEVELOPMENT:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_SEND_EMAIL = env('DEFAULT_SEND_EMAIL')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS')
    EMAIL_PORT = os.environ.get('EMAIL_PORT')
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_SEND_EMAIL = EMAIL_HOST_USER

WSGI_APPLICATION = f'{MAIN_APP}.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    # read os.environ['DATABASE_URL'] and raises
    # ImproperlyConfigured exception if not found
    #
    # The db() method is an alias for db_url().
    'default': env.db(),
}
if not TEST:
    # only need default database in test mode
    DATABASES.update({
        # read os.environ['REMOTE_DATABASE_URL']
        'remote': env.db_url(
            'REMOTE_DATABASE_URL',
            default=f'sqlite:'
                    f'///{os.path.join(BASE_DIR, "temp-remote.sqlite3")}'
        ),

        # read os.environ['SQLITE_URL']
        'extra': env.db_url(
            'SQLITE_URL',
            default=f'sqlite:'
                    f'///{os.path.join(BASE_DIR, "temp-sqlite.sqlite3")}'
        )
    })

# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-user-model
AUTH_USER_MODEL = f'{USER_APP_NAME}.User'

# 'allauth' site id
SITE_ID = int(env('SITE_ID'))
# 'allauth' provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    # For each OAuth based provider, either add a ``SocialApp``
    # (``socialaccount`` app) containing the required client
    # credentials, or list them here:
    "google": {
        # https://django-allauth.readthedocs.io/en/latest/providers.html#google
        "APP": {
        },
        # These are provider-specific settings that can only be
        # listed here:
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        }
    },
    # https://django-allauth.readthedocs.io/en/latest/providers.html#twitter
    "twitter": {
        "APP": {
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [{
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    }, {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
        'OPTIONS': {
            'min_length': MIN_PASSWORD_LEN,
        }
    }, {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]

# https://docs.djangoproject.com/en/4.1/ref/settings/#login-url
LOGIN_URL = USER_LOGIN_URL
# https://docs.djangoproject.com/en/4.1/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = f'{RECIPES_APP_NAME}:{RECIPE_HOME_ROUTE_NAME}'
# https://docs.djangoproject.com/en/4.1/ref/settings/#logout-redirect-url
LOGOUT_REDIRECT_URL = HOME_ROUTE_NAME

# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_USERNAME_MIN_LENGTH = 4
# needs route name (default value of settings.LOGIN_URL
# i.e. a url doesn't work [except '/'?])
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = LOGIN_ROUTE_NAME
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = HOME_ROUTE_NAME

# https://django-allauth.readthedocs.io/en/latest/forms.html
ACCOUNT_FORMS = {
    'signup': f'{USER_APP_NAME}.forms.UserSignupForm',
    'login': f'{USER_APP_NAME}.forms.UserLoginForm',
    'reset_password': f'{USER_APP_NAME}.forms.UserResetPasswordForm',
    'change_password': f'{USER_APP_NAME}.forms.UserChangePasswordForm',
    'add_email': f'{USER_APP_NAME}.forms.UserAddEmailForm',
}
# https://django-allauth.readthedocs.io/en/latest/forms.html#socialaccount-forms
SOCIALACCOUNT_FORMS = {
    'signup': f'{USER_APP_NAME}.forms.UserSocialSignupForm',
}

# https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-MESSAGE_TAGS
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
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

# fixtures
FIXTURE_DIRS = [
    os.path.join(BASE_DIR, 'data', 'fixtures')
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# url for placeholder images
AVATAR_BLANK_URL = env.get_value('AVATAR_BLANK_URL', default='')
RECIPE_BLANK_URL = env.get_value('RECIPE_BLANK_URL', default='')

DJANGO_LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'INFO').upper()
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    'formatters': {
        'verbose': {
            'format': '{name} {levelname} {asctime} {module} {process:d} '
                      '{thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': DJANGO_LOG_LEVEL,
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': DJANGO_LOG_LEVEL,
            'handlers': ['console'],
        },
        'django': {
            'handlers': ['console'],
            'level': DJANGO_LOG_LEVEL,
            'propagate': True,
        },
    }
}

# Google site verification
# https://support.google.com/webmasters/answer/9008080#meta_tag_verification&zippy=%2Chtml-tag
GOOGLE_SITE_VERIFICATION = env('GOOGLE_SITE_VERIFICATION', default='')

# Stripe configuration
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_KEY = env('STRIPE_WEBHOOK_KEY', default='')

# ISO 4217 code of the default currency
DEFAULT_CURRENCY = 'eur'
# number of decimal places to use during financial calculations
FINANCIAL_FACTOR = 6
# number of decimal places and digits to use for prices
PRICING_FACTOR = 2
PRICING_PLACES = 19

# Exchange Rates Data API
EXCHANGERATES_DATA_KEY = env('EXCHANGERATES_DATA_KEY', default='')
DEFAULT_RATES_REQUEST_INTERVAL = timedelta(days=1)

# Miscellaneous settings
FOOD_DOT_COM = env('FOOD_DOT_COM', default=False)
FACEBOOK_PAGE = env('FACEBOOK_PAGE', default="https://facebook.com")
