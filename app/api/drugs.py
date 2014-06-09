import app
import random

def declare_api():
    app.api.add_to_api('drug', app.models.Drug, ['GET'], primary_key='unique_id',
                       exclude_columns=['companies', 'id', 'creation_time'],
                       preprocessors={'GET_MANY':[restless_preprocessor_edited]},
                       postprocessors={'GET_SINGLE':[restless_postprocessor_filter_listings]})
    app.api.add_to_api('drug-max', app.models.Drug, ['GET'],
                       include_columns=['generic_name', 'label_name'], results_per_page=None)
    # Combine the following two into one
    app.api.add_to_api('typeahead-labels', app.models.Drug, ['GET'],
                       include_columns=['label_name'], results_per_page=None,
                       postprocessors={'GET_MANY':[restless_postprocessor_filter_typeahead]})
    app.api.add_to_api('typeahead-generics', app.models.Drug, ['GET'],
                       include_columns=['generic_name'], results_per_page=None,
                       postprocessors={'GET_MANY':[restless_postprocessor_filter_typeahead]})
    app.api.add_to_api('random-drugs', app.models.Drug, ['GET'],
                       include_columns=['generic_name', 'label_name'], results_per_page=None,
                       preprocessors={'GET_MANY':[restless_preprocessor_edited]},
                       postprocessors={'GET_MANY':[restless_postprocessor_randomize]})
    app.api.add_to_api('edit-drugs', app.models.Drug, ['GET'], results_per_page=50,
                       include_columns=['listings', 'generic_name', 'label_name', 'unique_id'],
                       preprocessors={'GET_MANY':[restless_preprocessor_unedited]},
                       postprocessors={'GET_MANY':[
                           restless_postprocessor_strength_and_form,
                           restless_postprocessor_orderby_generic_name
                           ]}
                       )

# Using the preprocessors instead of the filters caused a very large slowdown
# when operating with results_per_page=None. So it's fine for most things,
# but not for typeahead results
def restless_preprocessor_labels(search_params=None, **kw):
    _filter = dict(name='label_name', op='is_not_null')
    return app.api.restless_preprocessor(search_params, _filter, **kw)
def restless_preprocessor_generics(search_params=None, **kw):
    _filter = dict(name='label_name', op='is_null')
    return app.api.restless_preprocessor(search_params, _filter, **kw)
def restless_preprocessor_edited(search_params=None, **kw):
    _filter = dict(name='edited', op='==', val='True')
    return app.api.restless_preprocessor(search_params, _filter, **kw)
def restless_preprocessor_unedited(search_params=None, **kw):
    _filter = dict(name='edited', op='==', val='False')
    return app.api.restless_preprocessor(search_params, _filter, **kw)

def restless_postprocessor_filter_typeahead(result=None, search_params=None, **kw):
    def get_type_of_typeahead(params):
        for f in params['filters']:
            if f.get('name', '') == 'label_name' and f.get('op', '') == 'is_null':
                return 'generic_name'
            elif f.get('name', '') == 'label_name' and f.get('op', '') == 'is_not_null':
                return 'label_name'
        return None

    name_type = get_type_of_typeahead(search_params)
    if not name_type:
        result = result['objects']
    result['objects'] = [{'name':r[name_type].title(), 'type':name_type} for r in result['objects'] if search_params['query'].strip().lower() in r.get(name_type, '').lower()]

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


def restless_postprocessor_randomize(result=None, search_params=None, **kw):
    number = int(search_params['number'])
    _type = search_params['type']
    if _type == 'generic_name':
        drugs = [{'name':o[_type], 'type':_type} for o in result['objects'] if o.get(_type, None) != None and o.get('label_name') == None]
    elif _type == 'label_name':
        drugs = [{'name':o[_type], 'type':_type} for o in result['objects'] if o.get(_type, None) != None]
    random.shuffle(drugs)
    result['objects'] = [{'type':drug['type'], 'name':drug['name'].title()} for drug in drugs[:number]]

def restless_postprocessor_strength_and_form(result=None, search_params=None, **kw):
    drugs = result['objects']
    for drug in drugs:
        listings = drug['listings']
        if not listings or len(listings) == 0:
            drug['strength'] = None
            drug['form'] = None
        else:
            drug['strength'] = listings[0]['strength']
            drug['form'] = listings[0]['form']
            del drug['listings']
    result['objects'] = drugs

def restless_postprocessor_orderby_generic_name(result=None, search_params=None, **kw):
    result['objects'] = sorted(result['objects'], key=lambda d:d['generic_name'])
