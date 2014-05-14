import app
from flask import make_response

# routing for basic pages (pass routing onto the Angular app)
@app.flask_app.route('/')
@app.flask_app.route('/about')
def basic_pages(**kwargs):
    return make_response(open('app/templates/index.html').read())
