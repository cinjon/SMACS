import app
from flask import render_template

@app.flask_app.errorhandler(404)
def page_not_found(e):
    return render_template('smacs/404.html'), 404
