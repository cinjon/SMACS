import app
import os
from flask import send_from_directory

# special file handlers and error handlers
@app.flask_app.route('/favicon.ico')
def favicon():
    print app.flask_app.root_path
    return send_from_directory(os.path.join(app.flask_app.root_path, 'static'),
           'img/favicon.ico')
