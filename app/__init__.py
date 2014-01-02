from flask import Flask, g
# from flask.ext.login import LoginManager, current_user

flask_app = Flask(__name__)
flask_app.config.from_object('config')
flask_app.debug = True

# lm = LoginManager()
# lm.setup_app(flask_app)
# lm.login_view = 'home'

# @flask_app.before_request
# def before_request():
#     if current_user.is_anonymous():
#         g.user = None
#     else:
#         g.user = current_user

import views
import models
