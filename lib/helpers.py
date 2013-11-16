import os
import flask
import json
import functools
import ipset
import subprocess
import glob
import logging

__all__ = ['vpns_ipsets', 'flush_routing', 'flask_jsonify']

def vpns_ipsets(openvpn_config_path='/etc/openvpn'):
    """Walk through all openvpn configuration files in the given `openvpn_config_path' directory
    Create IpSet object for every config VPN configured there
        @return a dictionary of {'vpn_name': ipset_object, ...}
    """
    vpns = [os.path.splitext(os.path.basename(f))[0] for f in glob.glob('/etc/openvpn/*.conf')]
    ret = {}

    for vpn in vpns:
        try:
            ret[vpn] = ipset.IpSet(vpn)
        except ipset.IpSetException:
            logging.error("IPSET error for %s, check that the openvpn connection was successful", vpn)

    return ret

def flush_routing(ip):
    """Flushes the NATed connections for IP `ip'"""
    subprocess.check_call(['conntrack', '-D', '--orig-src', ip])
    subprocess.check_call(['ip', 'route', 'flush', ip])

def flask_jsonify(f):
    """Function decorator for flask routes. Jsonify the returned value"""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        return flask.Response(
            json.dumps(f(*args, **kwargs)),
            headers={'Content-Type': 'application/json'})

    return wrapped

