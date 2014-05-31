import app

def add_to_api(api_name, model, methods, **kwargs):
    # kwargs include include_columns, exclude_columns, primary_key, results_per_page ...
    # a results_per_page=None implies maximum returned
    d = {'model':model, 'methods':methods, 'collection_name':api_name}
    for key, value in kwargs.iteritems():
        d[key] = value
    app.flask_app.config['API_MODELS'][api_name] = d

def restless_preprocessor(search_params=None, filter=None, **kw):
    # Flask-Restless preprocessor parent function
    if search_params is None or filter is None:
        return
    if 'filters' not in search_params:
        search_params['filters'] = []
    search_params['filters'].append(filter)

import drugs
