import app
from flask import request, g
from flask.ext.login import current_user, login_required, logout_user

@app.lm.user_loader
def load_user(id):
    return app.models.kaizen_user.user_with_id(id)

@app.flask_app.before_request
def before_request():
    if current_user.is_anonymous():
        g.user = None
    else:
        g.user = current_user

@app.flask_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.is_xhr:
        email = request.form['email']
        password = request.form['password']
        if email=='' and password=='' and g.user:
            return app.utility.xhr_user_login(g.user, True)
        return app.models.kaizen_user.try_login(email, password, xhr=True)

@app.flask_app.route('/logout')
@login_required
def logout():
    if request.is_xhr:
        logout_user()
        return app.utility.xhr_response({}, 200)
