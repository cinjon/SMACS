from flask import Flask, request, Response
from flask import render_template, send_from_directory, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager
import utility
import config

basedir = config.basedir

flask_app = Flask(__name__)
flask_app.config.from_object('config')

db = SQLAlchemy(flask_app)
api_manager = APIManager(flask_app, flask_sqlalchemy_db=db)

@flask_app.before_first_request
def before_first_request():
    try:
        db.create_all()
    except Exception, e:
        flask_app.logger.error(str(e))

import models
import controllers
import process
