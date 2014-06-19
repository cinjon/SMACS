import app

@app.flask_app.route('/typeahead-canonical-names')
def typeahead_canonical_names():
    return app.utility.xhr_response({'data':list(set(c.canonical_name for c in app.models.CanonicalNames.query.all()))}, 200)
