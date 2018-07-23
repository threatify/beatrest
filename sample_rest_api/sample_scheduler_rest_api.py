from .bottle import Bottle, route, run, request, response, error, abort
import json
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import logging
debug = False

# MIME Types
MIME_JSON="application/json"

app = Bottle()
#Enable CORS
@app.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """

    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@app.route('/schedule', method='GET')
def get_schedule():

    schedule = {}


if __name__ == "__main__":
    run(app, reloader=True, host='localhost', port=8181, debug=True)
