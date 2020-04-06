"""
Django settings for receval project.
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import dj_database_url

from configurations import Configuration, importer, values
from configurations import importer
from django.contrib.messages import constants as message_constants
from django.utils.translation import ugettext_lazy as _

importer.install()

class Base(Configuration):
    SITE_NAME = values.Value('receval')
    # SITE_EMAIL = values.Value('hello@openlegaldata.io')
    SITE_URL = values.Value('http://localhost:8000')
    SITE_TITLE = values.Value('Recommender Evaluation')
    # SITE_ICON = values.Value('fa-balance-scale')
    # SITE_TWITTER_URL = values.Value('https://twitter.com/openlegaldata')
    # SITE_GITHUB_URL = values.Value('https://github.com/openlegaldata')
    # SITE_BLOG_URL = values.Value('//openlegaldata.io/blog')

    SITE_ID = values.IntegerValue(1)

    DEBUG = values.BooleanValue(True)

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Set project root for Heroku deployment
    # See https://devcenter.heroku.com/articles/django-assets
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = '__!7o-w9_5cyix-n%m-asg4=rtpcwh6rkoe6!d&yz2q%1y&fk5'

    ALLOWED_HOSTS = [
        '127.0.0.1',
        'localhost',
        'mieo.de',
        'receval.appserver24.com'
    ]


    # Application definition

    INSTALLED_APPS = [
        'receval.apps.explorer.apps.ExplorerConfig',
        'receval.apps.accounts.apps.AccountsConfig',

        # third-party
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'bootstrapform',
        'rest_framework.authtoken',

        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.sites',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.flatpages',
    ]

    MIDDLEWARE = [
        # Simplified static file serving.
        # https://warehouse.python.org/project/whitenoise/
        'whitenoise.middleware.WhiteNoiseMiddleware',

        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = 'receval.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(BASE_DIR, 'receval', 'assets', 'templates')
            ],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                    'receval.apps.explorer.apps.global_context_processor'
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'receval.wsgi.application'

    # Password validation
    # https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
    AUTHENTICATION_BACKENDS = (
        # Needed to login by username in Django admin, regardless of `allauth`
        'django.contrib.auth.backends.ModelBackend',

        # `allauth` specific authentication methods, such as login by e-mail
        'allauth.account.auth_backends.AuthenticationBackend',
    )
    LOGIN_REDIRECT_URL = '/accounts/email/'
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
    ACCOUNT_USERNAME_BLACKLIST = ['admin', 'oldp', 'openlegaldata']
    ACCOUNT_USERNAME_MIN_LENGTH = 3

    # Email settings
    DEFAULT_FROM_EMAIL = values.Value('no-reply@openlegaldata.io')
    # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST = values.Value('localhost')
    EMAIL_PORT = values.IntegerValue(25)
    EMAIL_USE_TLS = values.BooleanValue(False)
    EMAIL_HOST_USER = values.Value('')
    EMAIL_HOST_PASSWORD = values.Value('')

    # Internationalization
    # https://docs.djangoproject.com/en/1.11/topics/i18n/

    LANGUAGE_CODE = 'en-us'

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True


    # Database
    # https://docs.djangoproject.com/en/1.11/ref/settings/#databases
    DATABASES = {
        'default': {},
    }

    # Update database configuration with $DATABASE_URL.
    db_from_env = dj_database_url.config(conn_max_age=500, default='sqlite:///db.sqlite3')
    DATABASES['default'].update(db_from_env)
    #DATABASES['default']['TEST'] = {'NAME': DATABASES['default']['NAME']}

    # Domain for Wikipedia endpoint
    WIKI_DOMAIN = os.getenv('RECEVAL_WIKI', 'simple.wikipedia.org')

    # Honor the 'X-Forwarded-Proto' header for request.is_secure()
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.9/howto/static-files/
    STATIC_ROOT = os.path.join(BASE_DIR, 'receval/assets/static-dist')
    STATIC_URL = '/static/'

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

    # Extra places for collectstatic to find static files.
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'receval/assets/static')
    ]

    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/

    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    # ES Settings
    ES_INDEX = 'en-wp-ltr-0617_content'
    ES_TYPE = 'page'
    ES_URL = 'https://relforge1001.eqiad.wmnet:9243/en-wp-ltr-0617_content'
    ES_PROXY = {  # Use SSH tunnel
        'http': 'socks5h://localhost:1081',
        'https': 'socks5h://localhost:1081'
    }


    # Logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'console': {
                'format': '%(asctime)s %(levelname)-8s %(name)-12s %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'console',
            },
            'logfile': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'django.log'),
                'maxBytes': 1024*1024*15,  # 15MB
                'backupCount': 10,
                'formatter': 'console',
            },

            # Add Handler for Sentry for `warning` and above
            # 'sentry': {
            #     'level': 'WARNING',
            #     'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            # },
        },
        'loggers': {
            '': {  # root logger
                'level': 'INFO',
                'handlers': ['console', 'logfile'],
            },
            'receval': {
                'level': 'DEBUG',
            },
            'requests': {
                'level': 'ERROR'
            },
            'elasticsearch': {
                'level': 'ERROR'
            }
        },
    }

    # Messages

    MESSAGE_LEVEL = message_constants.DEBUG
    MESSAGE_TAGS = {
        message_constants.DEBUG: 'alert-info',
        message_constants.INFO: 'alert-info',
        message_constants.SUCCESS: 'alert-success',
        message_constants.WARNING: 'alert-warning',
        message_constants.ERROR: 'alert-danger',
    }

    # Recommender
    RECOMMENDATIONS_TOP_K = values.IntegerValue(0)

    # ZBMATH
    ZBMATH_DATABASE_URL = values.Value()
    ZBMATH_SSL_CERT = values.Value()
    ZBMATH_SSL_KEY = values.Value()
    ZBMATH_SSL_ROOTCERT = values.Value()


class Dev(Base):
    """Development settings (debugging enabled)"""
    DEBUG = True

    @property
    def INSTALLED_APPS(self):
        """Apps that are only available in debug mode"""
        return [
            'django_extensions',  # from generating UML chart

        ] + super().INSTALLED_APPS + [
            'debug_toolbar',
        ]

    @property
    def MIDDLEWARE(self):
        """Middlewares that are only available in debug mode"""
        return super().MIDDLEWARE + [
            'debug_toolbar.middleware.DebugToolbarMiddleware'
        ]


class Test(Base):
    """Use these settings for unit testing"""
    DEBUG = True

    DATABASES = values.DatabaseURLValue('sqlite:///test.db')
    # ELASTICSEARCH_INDEX = values.Value('oldp_test')

    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

    CACHE_DISABLE = True


class Prod(Base):
    """Production settings (override default values with environment vars"""
    SECRET_KEY = values.SecretValue()

    DEBUG = False

    # Set like this: DJANGO_ADMINS=Foo,foo@site.com;Bar,bar@site.com
    ADMINS = values.SingleNestedTupleValue()
