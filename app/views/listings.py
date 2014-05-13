import app
from flask import render_template, request, jsonify
# from flask.ext.login import logout_user, login_required, login_user

@app.flask_app.route('/listings', methods=['GET'])
def listings():
    return render_template('listings.html')
