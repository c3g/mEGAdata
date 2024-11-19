#mEGAdata configuration
SECRET_KEY = 'top_secret_key'
APPLICATION_PORT = 5000
APPLICATION_HOST = "127.0.0.1"
APPLICATION_DEBUG_MODE = True
APPLICATION_URL = 'http://megadata.vhost38.genap.ca'  # OAuth callback URL

#Database configuration
DATABASE_NAME = 'mEGAdata'
DATABASE_HOST = 'localhost'
DATABASE_USER = 'root'
DATABASE_PASSWORD = 'Same as for the IHEC Data Portal'

# Google OAuth configuration
GOOGLE_LOGIN_CLIENT_ID = '679553350748-m0j5683fobo96tj42mnchklh6424lupi.apps.googleusercontent.com'
GOOGLE_LOGIN_CLIENT_SECRET = ''
OAUTH_CREDENTIALS = {
    'google': {
        'id': GOOGLE_LOGIN_CLIENT_ID,
        'secret': GOOGLE_LOGIN_CLIENT_SECRET
    }
}
