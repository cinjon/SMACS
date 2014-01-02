import app
from flask import render_template, url_for, redirect, g
# from flask.ext.login import logout_user, login_required, login_user

@app.flask_app.route('/', methods=['GET'])
def home():
    return render_template('home.html')
