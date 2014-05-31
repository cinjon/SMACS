import app

# routing for API endpoints (generated from the models designated as API_MODELS)
for api_name, api_settings in app.flask_app.config['API_MODELS'].iteritems():
    app.api_manager.create_api(**api_settings)

import basic
import crud
import page_not_found
import favicon
import login
import home
