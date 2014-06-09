import app

def declare_api():
    app.api.add_to_api('typeahead-canonical-names', app.models.CanonicalNames, ['GET'],
                       include_columns=['canonical_name'])
