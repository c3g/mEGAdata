#mEGAdata configuration
SECRET_KEY = 'top_secret_key'
APPLICATION_PORT = 5000
APPLICATION_HOST = "127.0.0.1"
APPLICATION_DEBUG_MODE = True
APPLICATION_URL = 'http://localhost:5000'  # OAuth callback URL

#Database configuration
DATABASE_NAME = 'db_name'
DATABASE_HOST = 'localhost'
DATABASE_USER = 'megadata_user'
DATABASE_PASSWORD = 'passwd'

# Google OAuth configuration
GOOGLE_LOGIN_CLIENT_ID = '679553350748-m0j5683fobo96tj42mnchklh6424lupi.apps.googleusercontent.com'
GOOGLE_LOGIN_CLIENT_SECRET = '4K_etjtxSwh53wwUoM4ehYCh'
OAUTH_CREDENTIALS = {
    'google': {
        'id': GOOGLE_LOGIN_CLIENT_ID,
        'secret': GOOGLE_LOGIN_CLIENT_SECRET
    }
}
