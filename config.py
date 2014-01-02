import os
CSRF_ENABLED = True
SECRET_KEY = os.environ.get('COINBASE_SECRET_KEY')
basedir = os.path.abspath(os.path.dirname(__file__))
# SQLALCHEMY_DATABASE_URI = os.environ.get('COINBASE_DATABASE_URL')
