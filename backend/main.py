#!/usr/bin/env python
import connexion

app = connexion.App(__name__, specification_dir='../apis/paios/')

app.add_api('openapi.yaml')

if __name__ == '__main__':
    app.run(port=8080)
