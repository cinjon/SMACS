import app
from sqlalchemy.sql import exists
from flask import make_response, abort, jsonify

@app.flask_app.route('/drug/<drug_id>')
def drug(drug_id):
    if drug_id and app.api_manager.session.query(
        exists().where(app.models.Drug.unique_id == drug_id)).scalar():
        return make_response(open('app/public/template/smacs/index.html').read())
    abort(404)

@app.flask_app.route('/drug_unique_id/<drug_type>/<drug_name>')
def drug_unique_id(drug_type, drug_name):
     # Need to restrict this somehow so that only the site can access it and not a random scraper
     if drug_type == 'generic_name':
         drug = app.models.Drug.query.filter(app.models.Drug.generic_name == drug_name.upper(),
                                             app.models.Drug.label_name == None).first()
     elif drug_type == 'label_name':
         drug = app.models.Drug.query.filter(app.models.Drug.label_name == drug_name.upper()).first()
     if drug:
         return jsonify({'unique_id':drug.unique_id})
     return jsonify({'unique_id':''})
