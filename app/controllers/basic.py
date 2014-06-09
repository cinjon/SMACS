import app
from flask import make_response

# routing for basic pages (pass routing onto the Angular app)
@app.flask_app.route('/')
@app.flask_app.route('/about')
@app.flask_app.route('/home')
@app.flask_app.route('/edit')
def basic_pages(**kwargs):
    return make_response(open('app/public/template/smacs/index.html').read())
