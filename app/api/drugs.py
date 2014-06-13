import app
import random

@app.flask_app.route('/typeahead/<type_of_drug>')
def typeahead_labels(type_of_drug):
    if type_of_drug == 'label':
        ds = app.models.Drug.query.filter(
            app.models.Drug.label_name != None).all()
        return [d.label_name for d in ds]
    elif type_of_drug == 'generic':
        ds = app.models.Drug.query.filter(
            app.models.Drug.label_name == None).all()
        return [d.generic_name for d in ds]

@app.flask_app.route('/random-drugs/<type_of_drug>/<number>')
def random_drugs(type_of_drug, number):
    if type_of_drug == 'generic':
        ds = [
            {'name':d.generic_name} for d in app.models.Drug.query.all(
                app.models.Drug.edited == True,
                app.models.Drug.label_name == None
                ).all()
            ]
    elif type_of_drug == 'label':
        ds = [
            {'name':d.label_name} for d in app.models.Drug.query.all(
                app.models.Drug.edited == True,
                app.models.Drug.label_name != None
                ).all()
            ]
    random.shuffle(ds)
    return ds[:number]

@app.flask_app.route('/edit-drugs')
def edit_drugs():
    # order by name
    ds = app.models.Drug.query.filter(
        app.models.Drug.edited == False
        ).order_by(app.models.Drug.generic_name).limit(50)
    ds = [{
        'label_name':d.label_name, 'generic_name':d.generic_name,
        'strength':get_drug_key_from_listing(d, 'strength'),
        'form':get_drug_key_from_listing(d, 'form')
        } for d in ds]
    return ds

def get_drug_key_from_listing(drug, key):
    listings = drug.listings
    if not listings or len(listings) == 0:
        return None
    return listings[0].get(key)

def declare_api():
    app.api.add_to_api('drug', app.models.Drug, ['GET'], primary_key='unique_id',
                       exclude_columns=['companies', 'id', 'creation_time'],
                       preprocessors={'GET_MANY':[restless_preprocessor_edited]},
                       postprocessors={'GET_SINGLE':[restless_postprocessor_filter_listings]})

# Using the preprocessors instead of the filters caused a very large slowdown
# when operating with results_per_page=None. So it's fine for most things,
# but not for typeahead results
def restless_preprocessor_edited(search_params=None, **kw):
    _filter = dict(name='edited', op='==', val='True')
    return app.api.restless_preprocessor(search_params, _filter, **kw)

def restless_postprocessor_filter_listings(result=None, search_params=None, **kw):
    def filter_and_order_listings(listings):
        return [
            {'form':l.get('form', ''), 'ful':l.get('ful', ''), 'file':l.get('file_found'),
             'date':l.get('effective_date'), 'proposed':l.get('proposed', ''),
             'price':l.get('smac', ''), 'state':l['state'],
             'strength':l.get('strength', '')} for l in sorted(listings, key=lambda listing:listing.get('effective_date'), reverse=True)
            ]
    def check_for_key(listings, key):
        return any([l.get(key) for l in listings])

    if 'listings' in result:
        listings = result['listings']
        result['listings'] = filter_and_order_listings(listings)
        result['hasProposed'] = check_for_key(listings, 'proposed')
        result['hasForm'] = check_for_key(listings, 'form')
        result['hasFUL'] = check_for_key(listings, 'ful')
        result['hasStrength'] = check_for_key(listings, 'strength')
