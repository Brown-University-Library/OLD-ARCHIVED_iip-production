# -*- coding: utf-8 -*-

# Django settings for iip_smr_web_project.

import json, os


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['IIP_SMR__SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = json.loads( os.environ['IIP_SMR__DEBUG_JSON'] )  # will be True or False

# TEMPLATE_DEBUG = DEBUG

ADMINS = json.loads( os.environ['IIP_SMR__ADMINS_JSON'] )

ALLOWED_HOSTS = json.loads( os.environ.get(u'IIP_SMR__ALLOWED_HOSTS', '["127.0.0.1"]') )  # list

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.sites',
    'django.contrib.staticfiles',
    'crispy_forms',
    'markdown_deux',
    'pagedown',
    'iip_smr_web_app',
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

ROOT_URLCONF = 'iip_smr_config.urls'

TEMPLATES = json.loads( os.environ['IIP_SMR__TEMPLATES_JSON'] )  # list of dict(s)

WSGI_APPLICATION = 'iip_smr_config.passenger_wsgi.application'

# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = json.loads( os.environ['IIP_SMR__DATABASES_JSON'] )

# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
      'OPTIONS': { 'min_length': 9, }
      },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
    ]

# https://docs.djangoproject.com/en/1.11/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = os.environ['IIP_SMR__STATIC_URL']
STATIC_ROOT = os.environ['IIP_SMR__STATIC_ROOT']  # needed for collectstatic command

EMAIL_HOST = os.environ['IIP_SMR__EMAIL_HOST']
EMAIL_PORT = int( os.environ['IIP_SMR__EMAIL_PORT'] )

# <https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-SESSION_SAVE_EVERY_REQUEST>
# Thinking: not that many concurrent users, and no pages where session info isn't required, so overhead is reasonable.
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'logfile': {
            'level':'DEBUG',
            'class':'logging.FileHandler',  # note: configure server to use system's log-rotate to avoid permissions issues
            'filename': os.environ['IIP_SMR__LOG_PATH'],
            'formatter': 'standard',
        },
        # 'console':{
        #     'level':'DEBUG',
        #     'class':'logging.StreamHandler',
        #     'formatter': 'standard'
        # },
    },
    'loggers': {
        'iip_smr_web_app': {
            'handlers': ['logfile'],
            'level': 'DEBUG',
            'propogate': True
        },
    }
}


## for installed-app `markdown_deux` ##

MARKDOWN_DEUX_STYLES = {
    "default": {
        "extras": {
            "code-friendly": None,
            "footnotes": None,
        },
        "safe_mode": False,
    },
}
