#!/usr/bin/env python
import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))

import flask
import logging
from helpers import *

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')

app = flask.Flask(__name__, static_folder='static', static_url_path='')

vpns = vpns_ipsets()

@app.route('/')
def index():
    """Returns static/index.html"""
    return flask.send_from_directory(app.static_folder, "index.html")

@app.route('/api/vpns')
@flask_jsonify
def api_vpns():
    """Returns a JSON containing an array of all available VPNs"""
    return sorted(vpns.keys())

@app.route('/api/get')
def api_get():
    """Returns the currently used VPN"""
    membership = [name for name, vpn in vpns.items() if flask.request.remote_addr in vpn]
    return membership[0] if membership else ''

@app.route('/api/set/<name>')
def api_set(name):
    """Switch to VPN `name'

    Returns `name' if switched successfully, 404 if the VPN `name' does not exist
    """
    if not name in vpns:
        return ('No such vpn %s' % (name, ), 404)
    else:
        for vpn in vpns.values():
            if flask.request.remote_addr in vpn:
                vpn.remove(flask.request.remote_addr)

        vpns[name].add(flask.request.remote_addr)
        flush_routing(flask.request.remote_addr)

        return name

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
