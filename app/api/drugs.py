import app

# Using the preprocessors instead of the filters caused a very large slowdown
# when operating with results_per_page=None. So it's fine for most things,
# but not for typeahead results
def restless_preprocessor_labels(search_params=None, **kw):
    filter = dict(name='label_name', op='is_not_null')
    return app.api.restless_preprocessor(search_params, filter, **kw)
def restless_preprocessor_generics(search_params=None, **kw):
    filter = dict(name='label_name', op='is_null')
    return app.api.restless_preprocessor(search_params, filter, **kw)

def restless_postprocessor_drug_typeahead(result=None, search_params=None, **kw):
    _objects = result.get('objects', [])
    for _object in _objects:
        strength = _object.get('strength') or ''
        form = _object.get('form') or ''
        _object['strength_and_form'] = (strength + ' ' + form).strip()
        del _object['strength']
        del _object['form']
    result['objects'] = _objects
    return result

app.api.add_to_api('drug', app.models.Drug, ['GET'],
                   exclude_columns=['listings', 'companies'])
app.api.add_to_api('drug-max', app.models.Drug, ['GET'],
                   include_columns=['generic_name', 'label_name'], results_per_page=None)
app.api.add_to_api('typeahead-labels', app.models.Drug, ['GET'],
                   include_columns=['label_name', 'strength', 'form'], results_per_page=None,
                   postprocessors={'GET_MANY':[restless_postprocessor_drug_typeahead]})
app.api.add_to_api('typeahead-generics', app.models.Drug, ['GET'],
                   include_columns=['generic_name', 'strength', 'form'], results_per_page=None,
                   postprocessors={'GET_MANY':[restless_postprocessor_drug_typeahead]})
