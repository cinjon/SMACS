import os
CSRF_ENABLED = True
SECRET_KEY = os.environ.get('SMACS_SECRET_KEY')
basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
SQLALCHEMY_DATABASE_URI = os.environ.get('SMACS_DATABASE_URL', None)

# API Requests: gets filled in by /model and implemented by /controller
API_MODELS = {}
CRUD_URL_MODELS = {}
