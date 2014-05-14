import app

# routing for API endpoints (generated from the models designated as API_MODELS)
for model_name, model_class in app.flask_app.config['API_MODELS'].iteritems():
    app.api_manager.create_api(model_class, methods=['GET'])

import basic
import crud
import page_not_found
import favicon
