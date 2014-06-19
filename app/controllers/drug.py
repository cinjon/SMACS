import app
import random
from sqlalchemy.sql import exists
from flask import make_response, abort, request

@app.flask_app.route('/drug/<drug_id>')
def drug(drug_id):
    if drug_id and app.models.Drug.query.filter(app.models.Drug.unique_id == drug_id).first():
        return make_response(open('app/public/template/smacs/index.html').read())
    abort(404)

@app.flask_app.route('/drug-unique-id/<drug_type>/<drug_name>')
def drug_unique_id(drug_type, drug_name):
     # Need to restrict this somehow so that only the site can access it and not a random scraper
     if drug_type == 'generic':
         drug = app.models.Drug.query.filter(app.models.Drug.generic_name == drug_name.upper(),
                                             app.models.Drug.label_name == None).first()
     elif drug_type == 'label':
         drug = app.models.Drug.query.filter(app.models.Drug.label_name == drug_name.upper()).first()
     if drug:
         return app.utility.xhr_response({'unique_id':drug.unique_id}, 200)
     return app.utility.xhr_response({'unique_id':''}, 404)

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

    if response and response.get('success', False):
        if not 'deleted' in response:
            drug.edited = True
            app.db.session.commit()
        return app.utility.xhr_response(response, 200)
    return app.utility.xhr_response(response, 404)

def filter_and_order_listings(listings):
    def parse_key_value(key, listing):
        value = l.get(key, '')
        if key == 'effective_date' and value != '':
            return [value.day, value.month, value.year]
        return value
    return [{key:parse_key_value(key, l) for key in dir(l)} for l in sorted(listings, key=lambda listing:listing.effective_date)]

def check_for_key(listings, key):
    return any([l.get(key) for l in listings])

@app.flask_app.route('/get-drug/<drug_uid>')
def get_drug(drug_uid):
    drug = app.models.Drug.query.filter(app.models.Drug.unique_id == drug_uid).first()
    if not drug:
        app.utility.xhr_response({'success':False}, 404)
    ret = {}
    listings = drug.listings.all()
    ret['listings'] = filter_and_order_listings(listings)
    ret['hasProposed'] = check_for_key(listings, 'proposed')
    ret['hasFUL'] = check_for_key(listings, 'ful')
    ret['generic_name'] = drug.generic_name.title()
    if drug.label_name:
        ret['label_name'] = drug.label_name.title()
    else:
        ret['label_name'] = None
    return app.utility.xhr_response({'drug':ret, 'success':True}, 200)

@app.flask_app.route('/typeahead/<type_of_drug>/<user_input>')
def typeahead(type_of_drug, user_input):
    if not user_input or user_input == '':
        return app.utility.xhr_response({'success':False}, 404)

    user_input = user_input.lower()
    if type_of_drug == 'label':
        ds = app.models.Drug.query.filter(
            app.models.Drug.label_name != None, app.models.Drug.edited == True).all()
        data = [{'name':d.label_name, 'unique_id':d.unique_id} for d in ds if check_tokens_for_input(d.label_name.lower(), user_input)]
    elif type_of_drug == 'generic':
        ds = app.models.Drug.query.filter(
            app.models.Drug.label_name == None, app.models.Drug.edited == True).all()
        data = [{'name':d.generic_name, 'unique_id':d.unique_id} for d in ds if check_tokens_for_input(d.generic_name.lower(), user_input)]
    print data[:5]
    if data and len(data) > 0:
        return app.utility.xhr_response({'success':True, 'data':data}, 200)
    return app.utility.xhr_response({'success':False}, 400)

@app.flask_app.route('/get-random-drugs/<type_of_drug>/<number>')
def get_random_drugs(type_of_drug, number):
    number = int(number)
    if type_of_drug == 'generic':
        ds = [
            {'name':d.generic_name, 'type':'generic'} for d in app.models.Drug.query.filter(
                app.models.Drug.edited == True,
                app.models.Drug.label_name == None
                ).all()
            ]
    elif type_of_drug == 'label':
        ds = [
            {'name':d.label_name, 'type':'label'} for d in app.models.Drug.query.filter(
                app.models.Drug.edited == True,
                app.models.Drug.label_name != None
                ).all()
            ]
    random.shuffle(ds)
    return app.utility.xhr_response({'success':True, 'data':ds[:number]}, 200)

@app.flask_app.route('/get-edit-drugs')
def get_edit_drugs():
    # order by name
    ds = app.models.Drug.query.filter(
        app.models.Drug.edited == False
        ).order_by(app.models.Drug.generic_name).limit(50)
    ds = [{
        'label_name':d.label_name, 'generic_name':d.generic_name,
        'strength':get_drug_key_from_listing(d, 'strength'),
        'form':get_drug_key_from_listing(d, 'form')
        } for d in ds]
    return app.utility.xhr_response({'success':True, 'data':ds}, 200)

def get_drug_key_from_listing(drug, key):
    listings = drug.listings.all()
    if not listings or len(listings) == 0:
        return None
    return listings[0].get(key)

def check_tokens_for_input(name, input):
    return any([token[:len(input)] == input for token in name.split(' ')])
