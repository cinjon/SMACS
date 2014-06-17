import app
import random

def filter_and_order_listings(listings):
    def parse_key_value(key, listing):
        value = l.__dict__.get(key, '')
        if key == 'effective_date' and value != '':
            return [value.day, value.month, value.year]
        return value
    return [{key:parse_key_value(key, l) for key in dir(l)} for l in sorted(listings, key=lambda listing:listing.effective_date)]

def check_for_key(listings, key):
    return any([l.__dict__.get(key) for l in listings])

@app.flask_app.route('/get-drug/<drug_uid>')
def get_drug(drug_uid):
    drug = app.models.Drug.query.filter(app.models.Drug.unique_id == drug_uid).first()
    if not drug:
        app.utility.xhr_response({'success':False}, 404)
    ret = {}
    listings = drug.listings.all()
    ret['listings'] = filter_and_order_listings(listings)
    ret['hasProposed'] = check_for_key(listings, 'proposed')
    ret['hasForm'] = check_for_key(listings, 'form')
    ret['hasFUL'] = check_for_key(listings, 'ful')
    ret['hasStrength'] = check_for_key(listings, 'strength')
    ret['label_name'] = drug.label_name
    ret['generic_name'] = drug.generic_name

    return app.utility.xhr_response({'drug':ret, 'success':True}, 200)

@app.flask_app.route('/typeahead/<type_of_drug>/<user_input>')
def typeahead_labels(type_of_drug, user_input):
    if not user_input or user_input == '':
        return app.utility.xhr_response({'success':False}, 404)
    if type_of_drug == 'label':
        ds = app.models.Drug.query.filter(
            app.models.Drug.label_name != None).all()
        return app.utility.xhr_response({
            'success':True,
            'data':[{name:d.label_name, unique_id:d.unique_id} for d in ds if user_input in d.label_name]}, 200)
    elif type_of_drug == 'generic':
        ds = app.models.Drug.query.filter(
            app.models.Drug.label_name == None).all()
        return app.utility.xhr_response({
            'success':True,
            'data':[{name:d.generic_name, unique_id:d.unique_id} for d in ds if user_input in d.generic_name]}, 200)
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
    listings = drug.listings
    if not listings or len(listings) == 0:
        return None
    return listings[0].get(key)
