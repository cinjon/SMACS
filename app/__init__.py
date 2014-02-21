from flask import Flask, g
from flask.ext.sqlalchemy import SQLAlchemy
import utility


flask_app = Flask(__name__)
flask_app.config.from_object('config')
flask_app.debug = True
db = SQLAlchemy(flask_app)

@flask_app.before_first_request
def before_first_request():
    try:
        db.create_all()
    except Exception, e:
        flask_app.logger.error(str(e))

import views
import models
import ops
