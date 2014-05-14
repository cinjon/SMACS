import app
from sqlalchemy.sql import exists
from flask import make_response, abort

# routing for CRUD-style endpoints
# passes routing onto the angular frontend if the requested resource exists

session = app.api_manager.session
crud_url_models = app.flask_app.config['CRUD_URL_MODELS']

@app.flask_app.route('/<model_name>/')
@app.flask_app.route('/<model_name>/<item_id>')
def rest_pages(model_name, item_id=None):
    model_class = crud_url_models.get(model_name)
    if not model_class:
        abort(404)
    if item_id is None or session.query(
        exists().where(model_class.id == item_id)).scalar():
        print 'hi in make_response'
        return make_response(open(
            'app/templates/index.html').read())
    abort(404)
