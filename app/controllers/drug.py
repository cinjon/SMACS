import app
from sqlalchemy.sql import exists
from flask import make_response, abort, jsonify, request

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

@app.flask_app.route('/edit-drug', methods=['GET', 'POST'])
def edit_drug():
    generic_name = request.form.get('generic_name').strip()
    label_name = request.form.get('label_name').strip()
    unique_id = request.form.get('unique_id').strip()
    strength = request.form.get('strength').strip()
    form = request.form.get('form').strip()

    if not unique_id:
        return app.utility.xhr_response({'success':False}, 404)

    drug = app.models.Drug.query.filter(app.models.Drug.unique_id==unique_id).first()
    if not drug or (label_name == '' and drug.label_name != None) or (generic_name == ''):
        return app.utility.xhr_response({'success':False}, 404)

    drug.set_listing_attributes(strength, form)
    if drug.label_name:
        response = app.models.set_canonical_label_name(drug, label_name, generic_name, strength, form)
    else:
        response = app.models.set_canonical_generic_name(drug, generic_name, strength, form)

    if response['success']:
        if not 'deleted' in response:
            drug.edited = True
            app.db.session.commit()
        return app.utility.xhr_response(response, 200)
    return app.utility.xhr_response(response, 404)
