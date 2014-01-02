from flask import Flask, g

flask_app = Flask(__name__)
flask_app.config.from_object('config')
flask_app.debug = True

import views
import models

order_book = models.OrderBook()
order_book.request_orders()
