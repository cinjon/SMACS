import app

@app.flask_app.route('/typeahead-canonical-names')
def typeahead_canonical_names():
    ds = app.models.CanonicalNames.query.with_entities(
        app.models.CanonicalNames.canonical_name).all()
    return list(set(d['canonical_name'] for d in ds))
