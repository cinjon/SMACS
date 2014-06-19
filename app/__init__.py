from flask import Flask, request, Response
from flask import render_template, send_from_directory, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
# from flask.ext.security import Security, SQLAlchemyUserDatastore
import utility
import config

basedir = config.basedir

flask_app = Flask(__name__, template_folder='public/template')
flask_app.config.from_object('config')

db = SQLAlchemy(flask_app)

lm = LoginManager()
lm.setup_app(flask_app)
lm.login_view = 'index'

@flask_app.before_first_request
def before_first_request():
    try:
        db.create_all()
    except Exception, e:
        flask_app.logger.error(str(e))

import models
# security_ds = SQLAlchemyUserDatastore(db, models.kaizen_user.KaizenUser, models.role.Role)
# security = Security(flask_app, security_ds)
# flask_app.security = security

import controllers
import process
