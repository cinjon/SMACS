from flask import Flask, g
import datetime
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

order_book = models.OrderBook()
order_book.request_orders()
print datetime.datetime.fromtimestamp(float(order_book.get_last_updated())).strftime('%Y-%m-%d %H:%M:%S')
