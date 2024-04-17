#!/usr/bin/env python
import connexion
from flask_cors import CORS

app = connexion.App(__name__, specification_dir='../apis/paios/')
CORS(app.app, expose_headers='X-Total-Count')

app.add_api('openapi.yaml')

if __name__ == '__main__':
    app.run(port=3000)
