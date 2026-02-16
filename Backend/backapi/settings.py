from pathlib import Path
import os
import sys
import pymysql

pymysql.install_as_MySQLdb()

# Base directory (Backend/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

# Security: Trust the 'X-Forwarded-Proto' header for determining SSL (Traefik handles this)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Quick development settings - replace for production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-prod')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
if 'test' in sys.argv:
    ALLOWED_HOSTS.append('testserver')

# SSL/HTTPS & Cookies
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = False # Handled by Traefik, but good to have if direct
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000 # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'accounts',
    'families',
    'news',
    'profiles',
]

REST_FRAMEWORK = {
    # Use standard permission classes if needed default
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backapi.urls'

CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')

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

WSGI_APPLICATION = 'backapi.wsgi.application'

if os.environ.get('DB_ENGINE') == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }
elif os.environ.get('POSTGRES_DB'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('POSTGRES_HOST'),
            'PORT': os.environ.get('POSTGRES_PORT', 5432),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'accounts.validators.ComplexPasswordValidator',
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

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR / 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging Configuration for Production
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
            'filename': BASE_DIR / 'django_error.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Use the custom user model defined in the `accounts` app
AUTH_USER_MODEL = 'accounts.User'

UNFOLD = {
    "SITE_TITLE": "Kollamparambil Family Admin",
    "SITE_HEADER": "Kollamparambil Family",
    "SITE_SYMBOL": "family_restroom", # Material symbol
    "ENVIRONMENT": "backapi.utils.get_environment",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "250 245 239",
            "100": "241 230 214",
            "200": "225 204 172",
            "300": "202 168 120",
            "400": "179 133 79",
            "500": "160 128 80", # #A08050
            "600": "139 104 63",
            "700": "116 82 51",
            "800": "95 68 45",
            "900": "79 57 39",
            "950": "43 30 19",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Authentication",
                "separator": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "manage_accounts", 
                        "link": "reverse:admin:accounts_user_changelist",
                    },
                    {
                        "title": "Invite Tokens",
                        "icon": "vpn_key", 
                        "link": "reverse:admin:accounts_invitetoken_changelist",
                    },
                ],
            },
            {
                "title": "Family Directory",
                "separator": True,
                "items": [
                    {
                        "title": "Families",
                        "icon": "family_restroom",
                        "link": "reverse:admin:families_family_changelist",
                    },
                    {
                        "title": "Heads of Family",
                        "icon": "supervisor_account",
                        "link": "reverse:admin:families_familyhead_changelist",
                    },
                    {
                        "title": "Members",
                        "icon": "group",
                        "link": "reverse:admin:families_familymember_changelist",
                    },
                    {
                        "title": "Deceased",
                        "icon": "hourglass_empty",
                        "link": "reverse:admin:families_deceasedmember_changelist",
                    },
                ],
            },
            {
                "title": "Content Management",
                "separator": True,
                "items": [
                    {
                        "title": "News & Events",
                        "icon": "newspaper",
                        "link": "reverse:admin:news_post_changelist",
                    },
                    {
                        "title": "Post Media",
                        "icon": "perm_media",
                        "link": "reverse:admin:news_media_changelist",
                    },
                ],
            },
            {
                "title": "Gallery & Committee",
                "separator": True,
                "items": [
                    {
                        "title": "Photo Gallery",
                        "icon": "photo_library",
                        "link": "reverse:admin:profiles_gallery_changelist",
                    },
                    {
                        "title": "Family Media",
                        "icon": "collections",
                        "link": "reverse:admin:families_familymedia_changelist",
                    },
                    {
                        "title": "Committee",
                        "icon": "work",
                        "link": "reverse:admin:profiles_committee_changelist",
                    },
                ],
            },
        ],
    },
}
