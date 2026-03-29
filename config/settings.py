"""
Django settings for config project.
Optimized for 512MB memory constraint (Render free tier).
"""

from pathlib import Path
import os
import dj_database_url
from datetime import timedelta

# ============================================================
# BASE DIR
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================
# SECURITY
# ============================================================
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

# CRITICAL for memory: Disable DEBUG in production
# DEBUG = True causes verbose error pages, verbose logging, disables optimizations
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS - comprehensive list for all deployment scenarios
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'analytics-backend-3f79.onrender.com',  # Your specific Render domain
    '.onrender.com',                         # Wildcard for other Render subdomains
    'analytics-dashboard-ten-delta.vercel.app',  # Frontend domain
]

# Allow environment variable override if needed (for testing/custom domains)
if os.environ.get('ALLOWED_HOSTS'):
    env_hosts = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]
    ALLOWED_HOSTS.extend(env_hosts)

# ============================================================
# APPLICATIONS (MINIMAL SET)
# ============================================================
# For REST API with JWT: We don't need Django's session-based auth or admin
# Removed: django.contrib.admin (not needed for REST API)
# Removed: django.contrib.sessions (not needed with JWT)
# Removed: django.contrib.messages (not needed for API)
# Kept: Only essential components for auth model and ORM
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 'django.contrib.admin',  # REMOVED: Not needed for REST API
    # 'django.contrib.sessions',  # REMOVED: Not needed with JWT auth
    # 'django.contrib.messages',  # REMOVED: Not needed for API
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'corsheaders',

    # Local
    'users.apps.UsersConfig',
    'analytics.apps.AnalyticsConfig',
    'api.apps.ApiConfig',
]

# ============================================================
# MIDDLEWARE (MINIMAL SET)
# ============================================================
# For REST API with JWT: Session and auth middleware not needed
# Removed: SessionMiddleware (JWT doesn't use sessions)
# Removed: AuthenticationMiddleware (JWT handled by DRF, not Django middleware)
# Removed: MessageMiddleware (not needed for API)
# Kept: Only security-critical and functional middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    # 'django.contrib.sessions.middleware.SessionMiddleware',  # REMOVED
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',  # REMOVED: DRF handles auth
    # 'django.contrib.messages.middleware.MessageMiddleware',  # REMOVED
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
AUTH_USER_MODEL = 'users.CustomUser'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                # 'django.contrib.messages.context_processors.messages',  # REMOVED
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ============================================================
# DATABASE
# ============================================================
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Production (Render PostgreSQL)
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,  # Connection pooling
            ssl_require=True
        )
    }
else:
    # Local (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Database query optimization
# ATOMIC_REQUESTS = False  # Use explicit transactions for better control
# CONN_MAX_AGE already set in dj_database_url

# ============================================================
# PASSWORD VALIDATION (MINIMAL)
# ============================================================
# Reduced validators for faster registration without sacrificing security
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
]

# ============================================================
# REST FRAMEWORK
# ============================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,  # CRITICAL: Reduced from 50 to 25 to prevent memory spikes
    'MAX_PAGE_SIZE': 50,  # Hard cap: never return more than 50 items
}

# ============================================================
# JWT
# ============================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ============================================================
# CORS
# ============================================================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://analytics-dashboard-ten-delta.vercel.app",
    "analytics-backend-3f79.onrender.com",
]

CORS_ALLOW_CREDENTIALS = True

# ============================================================
# SECURITY SETTINGS
# ============================================================
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True') == 'True'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'True') == 'True'
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 31536000))

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
    "https://analytics-dashboard-ten-delta.vercel.app"
]

# ============================================================
# STATIC FILES
# ============================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ============================================================
# INTERNATIONALIZATION
# ============================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# CACHING (LIGHTWEIGHT IN-MEMORY)
# ============================================================
# Use Django's local memory cache for analytics endpoint caching
# This reduces database hits without adding Redis dependency (saves memory)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'memory-cache',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 1000  # Prevent unbounded cache growth
        }
    }
}

# Cache timeout for analytics endpoint (balance freshness vs. memory)
ANALYTICS_CACHE_TIMEOUT = 60  # 60 seconds for analytics queries

# ============================================================
# LOGGING (MINIMAL - CRITICAL FOR MEMORY)
# ============================================================
# CRITICAL: Default Django logging is VERBOSE and creates memory overhead
# Set WARNING level to suppress debug info, SQL queries, etc.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,  # Disable all default loggers
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',  # Only log WARNING and above (ERROR, CRITICAL)
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',  # Suppress SQL query logging
            'propagate': False,
        },
    },
}