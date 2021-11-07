import _locale
import os
from datetime import timedelta
from django.core.management.utils import get_random_secret_key
import environ
from kombu import Exchange, Queue

root = environ.Path(__file__) - 2

# setting roots for static, media, templates
templates_root = root('templates')
LOGGING = {
	'version'                 : 1,
	'disable_existing_loggers': False,
	'formatters'              : {
		'default': {
			'format': '[DJANGO] %(levelname)s %(asctime)s %(module)s '
					  '%(name)s.%(funcName)s:%(lineno)s: %(message)s'
		},
	},
	'handlers'                : {
		'console': {
			'level'    : 'DEBUG',
			'class'    : 'logging.StreamHandler',
			'formatter': 'default',
		}
	},
	'root'                    : {
		'handlers': ['console'],
		'level'   : 'WARNING',
	},
	'loggers'                 : {
		'*'     : {
			'handlers' : ['console'],
			'level'    : 'DEBUG',
			'propagate': True,
		},
		'django': {
			'handlers' : ['console'],
			'level'    : os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
			'propagate': False,
		},
	},
}
env = environ.Env()
# reading env file
environ.Env.read_env(env_file=root('.env'))
# site root points to rainshop root folder
SITE_ROOT = root()
DEBUG = env.bool('DEBUG', default=True)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CORS_ALLOW_CREDENTIALS = True
SECRET_KEY = env.str('SECRET_KEY', default=get_random_secret_key())
ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='127.0.0.1,.localhost').split(',')
ADMINS = env.list('ADMINS', default=[('Yury Borodin', 'yuiborodin@gmail.com')])
CORS_ORIGIN_ALLOW_ALL = env.bool('CORS_ORIGIN_ALLOW_ALL', default=True)
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS',
								default=['http://127.0.0.1:8000', 'http://localhost:8000'])
USE_REDIS_CACHE = env.bool('USE_REDIS_CACHE', default=False)

ROOT_URLCONF = 'rainshop.urls'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True
APPEND_SLASH = True
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
WSGI_APPLICATION = 'rainshop.wsgi.application'
TEMPLATES = [
	{
		'BACKEND' : 'django.template.backends.django.DjangoTemplates',
		'DIRS'    : ['templates'],
		'APP_DIRS': True,
		'OPTIONS' : {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

INSTALLED_APPS = [
	# DJANGO BUILTINS #
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'rest_framework.authtoken',
	# EXTERNAL APPS #
	'drf_yasg',
	'rest_framework',
	'debug_toolbar',
	'djmoney',
	'rest_framework_swagger',
	'watchman',
	'django_filters',
	'corsheaders',
	# APPS #
	'products',
	'cart',
	'orders'
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

DEFAULT_RENDERER_CLASSES = (
	'rest_framework.renderers.JSONRenderer',
)
if DEBUG:
	MIDDLEWARE += [
		'debug_toolbar.middleware.DebugToolbarMiddleware',
	]
	INTERNAL_IPS = ['127.0.0.1', ]

	# this is the main reason for not showing up the toolbar
	import mimetypes

	mimetypes.add_type("application/javascript", ".js", True)

	DEBUG_TOOLBAR_CONFIG = {
		'INTERCEPT_REDIRECTS': False,
	}
	DEFAULT_RENDERER_CLASSES = DEFAULT_RENDERER_CLASSES + (
		'rest_framework.renderers.BrowsableAPIRenderer',
	)
AUTHENTICATION_BACKENDS = [
	'django.contrib.auth.backends.ModelBackend',
]
REST_FRAMEWORK = {
	'DEFAULT_PERMISSION_CLASSES'    : [
		'rest_framework.permissions.AllowAny',
	],
	'DEFAULT_PARSER_CLASSES'        : [
		'rest_framework.parsers.JSONParser',
	],
	'DEFAULT_THROTTLE_CLASSES'      : [
		'rest_framework.throttling.AnonRateThrottle',
		'rest_framework.throttling.UserRateThrottle',
		'rest_framework.throttling.ScopedRateThrottle',
	],
	'DEFAULT_THROTTLE_RATES'        : {
		'anon': '250/minute',
		'user': '250/minute'
	},
	'DATETIME_FORMAT'               : '%Y-%m-%dT%H:%M:%S%z',
	'DEFAULT_AUTHENTICATION_CLASSES': [
		'rest_framework.authentication.TokenAuthentication',
		'rest_framework.authentication.SessionAuthentication',
	],

	'DEFAULT_PAGINATION_CLASS'      : 'rest_framework.pagination.LimitOffsetPagination',
	'PAGE_SIZE'                     : 50,

	'DEFAULT_RENDERER_CLASSES'      : DEFAULT_RENDERER_CLASSES
}
USE_POSTGRES = env.bool('USE_POSTGRES', False)
if USE_POSTGRES:
	DATABASES = {
		'default': {
			'ENGINE'  : 'django.db.backends.postgresql',
			'NAME'    : env('DB_NAME'),
			'USER'    : env('DB_USER'),
			'PASSWORD': env('DB_PASSWORD'),
			'HOST'    : env('DB_HOST'),
			'PORT'    : env('DB_PORT'),
			'OPTIONS' : {
				'options': '-c search_path=public'
			}
		}
	}
else:
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.sqlite3',
			'NAME'  : 'db1.sqlite3',
		}
	}

if env.bool('SQL_DEBUG', False):
	MIDDLEWARE += ['sql_middleware.SqlPrintingMiddleware']

if USE_REDIS_CACHE:
	CACHE_TTL = 60 * 1

	CACHES = {
		'default': {
			'BACKEND'   : 'django_redis.cache.RedisCache',
			'LOCATION'  : env('CACHE_URL_1'),
			'OPTIONS'   : {
				'CLIENT_CLASS': 'django_redis.client.DefaultClient',
			},
			'KEY_PREFIX': 'pr_chc'
		}
	}
	SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
	SESSION_CACHE_ALIAS = 'default'

else:
	CACHE_TTL = 60 * 1
	CACHES = {
		'default': {
			'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
		}
	}
	SESSION_CACHE_ALIAS = 'default'

SITE_ID = 1
INTERNAL_IPS = ['127.0.0.1', ]

if DEBUG:
	STATIC_ROOT = root('static')
	STATIC_URL = '/static/'
else:
	STATIC_URL = '/static/'
	STATIC_ROOT = env.str('STATIC_ROOT', default=root('static'))
MEDIA_ROOT = root('media')
MEDIA_URL = '/media/'

CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default='redis://127.0.0.1:6379')
CELERY_RESULT_BACKEND = env.str('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'

default_exchange = Exchange('default', type='direct')

CELERY_QUEUES = (
	Queue('default', default_exchange, routing_key='default', consumer_arguments={'x-priority': 0}),
)
CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_IGNORE_RESULT = False
CELERY_TRACK_STARTED = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
# AXES SETTINGS
AXES_FAILURE_LIMIT = 7
AXES_LOCK_OUT_AT_FAILURE = True
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_RESET_ON_SUCCESS = True
AXES_COOLOFF_TIME = 24
AXES_META_PRECEDENCE_ORDER = [
	'HTTP_X_FORWARDED_FOR',
]
