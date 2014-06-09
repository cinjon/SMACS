import app

def declare_api():
    app.api.add_to_api('typeahead-canonical-names', app.models.CanonicalNames, ['GET'],
                       include_columns=['canonical_name', 'name_as_key'],
                       postprocessors={'GET_MANY':[restless_postprocessor_deduplicate]})

def restless_postprocessor_deduplicate(result=None, search_params=None, **kw):
    print result['objects']
    result['objects'] = list(set([n['canonical_name'] for n in result['objects']]))
