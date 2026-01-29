"""
Django settings for premises project.
Adjusted for Production Deployment with Traefik and Docker.
"""

from pathlib import Path
from datetime import timedelta
import os
import dj_database_url # Add this to requirements.txt for easier DB parsing
from dotenv import load_dotenv
load_dotenv()  

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- PRODUCTION SECURITY SETTINGS ---
# Get from environment variable or use a fallback for dev only
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-m0zek1twsjfahyn&hsk1dngm_=v^v))u0h%ls*3&$4j_8$_d2p')

# Turn DEBUG off in production
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Add your VPS domains here
ALLOWED_HOSTS = [
    'arthiproperties.mkon.tech',
    '127.0.0.1', 
    'localhost',
]

# Essential for Traefik/HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'django.contrib.humanize',
    'listings',
    'core',
    'booking',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Recommended for static files in Docker
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'premises.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'listings' / 'templates', 
            BASE_DIR / 'templates', 
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'premises.wsgi.application'

# --- DATABASE CONFIGURATION ---
# Switched from SQLite to PostgreSQL (Docker)
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- STATIC & MEDIA FILES ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] 

# WhiteNoise storage for efficient serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'                    
MEDIA_ROOT = BASE_DIR / 'media'          

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

CORS_ALLOW_ALL_ORIGINS = DEBUG # Only allow all in Dev
if not DEBUG:
    CORS_ALLOWED_ORIGINS = [
        "https://realestate.mkon.tech",
        # Add your frontend URL here
    ]
CORS_ALLOW_CREDENTIALS = True

# JAZZMIN SETTINGS
JAZZMIN_SETTINGS = {
    "site_title": "ArthiProperties Admin",
    "site_header": "ArthiProperties",
    "site_brand": "ArthiProperties",
    "welcome_sign": "Welcome to the HQ",
    "copyright": "ArthiProperties Ltd",
    "search_model": ["listings.Property", "auth.User"],
    "user_avatar": None,
    "custom_css": "css/admin_theme.css",
    "show_ui_builder": False,
}

# EMAIL SETTINGS
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "login"