import os
from pathlib import Path
from dotenv import load_dotenv
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

# ---- SECURITY ----
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ---- SENTRY ----
import sentry_sdk
if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        environment='production' if not DEBUG else 'development',
    )
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') + ['.ngrok-free.dev', '.ngrok-free.app', '.ngrok.io']
CSRF_TRUSTED_ORIGINS = [o for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o] if os.getenv('CSRF_TRUSTED_ORIGINS') else []

if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True') == 'True'
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True') == 'True'
    SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'True') == 'True'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_CONTENT_TYPE_NOSNIFF = True

# ---- APPLICATIONS ----
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',

    # Third-party
    'crispy_forms',
    'crispy_bootstrap5',
    'corsheaders',
    'axes',

    'django_ses',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'django_celery_beat',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',

    # Local apps
    'products',
    'cart',
    'orders',
    'coupons',
    'payments',
    'delivery',
    'notifications',
    'dashboard',
    'api',
    'analytics',
    'chatbot',
    'users',
    'blog',
    'pages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'macgunjon.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'cart.context_processors.cart_context',
                'dashboard.context_processors.site_settings',
                'dashboard.context_processors.nav_categories',
                'dashboard.context_processors.notification_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'macgunjon.wsgi.application'

# ---- DATABASE ----
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'macgunjon'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '600')),
    }
}

# ---- AUTH ----
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# Allauth settings
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_SESSION_REMEMBER = True

SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = ACCOUNT_EMAIL_VERIFICATION
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'FIELDS': ['id', 'email', 'name', 'first_name', 'last_name', 'picture'],
        'EXCHANGE_TOKEN': True,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'products:product_list'
LOGOUT_REDIRECT_URL = 'products:product_list'

# ---- CACHE & SESSIONS ----
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
if os.getenv('REDIS_URL'):
    CACHES['default'] = {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'

# ---- INTERNATIONALIZATION ----
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('en-us', 'English (US)'),
    ('en-gb', 'English (UK)'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

os.makedirs(BASE_DIR / 'locale', exist_ok=True)
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ---- CELERY ----
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Dhaka'

CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-delivery-tokens': {
        'task': 'delivery.tasks.cleanup_expired_tokens',
        'schedule': crontab(hour=3, minute=0),
    },
    'cleanup-old-pending-orders': {
        'task': 'orders.tasks.cleanup_old_carts',
        'schedule': crontab(hour=4, minute=0),
    },
    'generate-daily-sales-report': {
        'task': 'analytics.tasks.generate_daily_report',
        'schedule': crontab(hour=5, minute=0),
    },
}

# ---- REST FRAMEWORK ----
from datetime import timedelta
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '50/hour',
        'user': '200/hour',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# ---- STATIC & MEDIA ----
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ---- CRISPY FORMS ----
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ---- CORS ----
CORS_ALLOWED_ORIGINS = [o for o in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if o] if os.getenv('CORS_ALLOWED_ORIGINS') else []
CORS_ALLOW_CREDENTIALS = True

# ---- AXES (Brute-force protection) ----
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1
AXES_LOCKOUT_TEMPLATE = 'errors/403.html'
AXES_RESET_ON_SUCCESS = True

# ---- SESSION ----
SESSION_COOKIE_AGE = 86400  # 1 day in seconds

# ---- STRIPE ----
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')

CART_SESSION_ID = 'cart'

# ---- EMAIL ----
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('BREVO_EMAIL_HOST', 'smtp-relay.brevo.com')
EMAIL_PORT = int(os.getenv('BREVO_EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('BREVO_EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('BREVO_EMAIL_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('BREVO_SMTP_KEY', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Mac GunJon <noreply@macgunjon.com>')

# Site URL for absolute links in emails
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')

# ---- LOGGING ----
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO' if DEBUG else 'ERROR',
            'propagate': True,
        },
    },
}

for _app in ['products', 'orders', 'payments', 'users', 'cart', 'chatbot', 'coupons', 'delivery', 'notifications', 'analytics', 'dashboard', 'blog', 'pages', 'api']:
    LOGGING['loggers'][_app] = {
        'handlers': ['file', 'console'],
        'level': 'INFO' if DEBUG else 'ERROR',
        'propagate': False,
    }

# ---- DEFAULT AUTO FIELD ----
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
