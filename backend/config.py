from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

SESSION_TYPE = 'redis'
SESSION_USE_SIGNER = True
SESSION_COOKIE_SECURE = False # Use True if your app is served over HTTPS 
SESSION_COOKIE_HTTPONLY = True 
SESSION_COOKIE_SAMESITE = 'Lax'
UPLOAD_FOLDER = '/tmp'
SECRET_KEY = environ.get('SECRET_KEY')
