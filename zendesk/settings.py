SECRET_KEY = 'secret'

API_TOKEN = 'secret'

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

CELERY_BROKER_URL = 'redis://localhost:6379/0'

ZENDESK_URL = 'https://domain.zendesk.com'
ZENDESK_EMAIL = 'user@domain.com'
ZENDESK_TOKEN = 'secret'

ZENDESK_FIELD_IDS = {
    'start_date': 24462829,
    'start_time': 24435179,
    'end_date': 24524155,
    'end_time': 24500385
}

GOOGLE_CLIENT_ID = 'secret.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'secret'
GOOGLE_REQUEST_SCOPE = 'https://www.googleapis.com/auth/calendar'
