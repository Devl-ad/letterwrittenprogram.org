from pathlib import Path


import os
import environ

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # 2FA
    # 'django_otp',
    # 'django_otp.plugins.otp_totp',
    # 'two_factor',
    # Local apps
    "apps.adminpanel",
    "apps.accounts",
    "apps.letters",
    "apps.payments",
    "apps.dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "smartwriting.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.adminpanel.context_processors.admin_counts",
            ],
        },
    }
]

WSGI_APPLICATION = "smartwriting.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = "/home/lettfgal/public_html/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

# LOGIN_URL          = 'two_factor:login'
# LOGIN_REDIRECT_URL = 'dashboard:index'
# LOGOUT_REDIRECT_URL = 'two_factor:login'
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard:index"
LOGOUT_REDIRECT_URL = "login"


# Per-letter payout amount
LETTER_APPROVAL_PAYMENT = 95.50

# Crypto deposit wallets — replace with your real addresses

CRYPTO_WALLETS = {
    "BTC": "bc1qucr0dpzhj6z8uk8j9ydt02c8pa7z2939mqeuet",
    "USDT": "TEenN3dD4uQXNzbXaEKxua5Z8Ct8kdVWLj",
    "ETH": "0x0A6B86f2E9A57397161d9e79453fa21Aacd37508",
}


EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
EMAIL_USE_SSL = False

# Highly recommended extras
# must match EMAIL_HOST_USER or a verified alias
SERVER_EMAIL = "info@letterwrittenprogram.org"

# Optional but helps deliverability
EMAIL_SUBJECT_PREFIX = "letterwrittenprogram.org"  # makes it look less spammy
