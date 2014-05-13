import app
from flask import request, jsonify, render_template
import flask.views

@app.flask_app.route('/')
def home():
    return make_response(open('home.html').read())
