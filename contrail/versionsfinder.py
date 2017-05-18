# This program query the contrail-api endpoints (REST API) to get the build version details
# http://analytics-api:8081/analytics/uves
# vrouters
# control-nodes
# config-nodes
# analytics-nodes
"""

1.Query vrouter endpoint.
2.Get the list of vrouters in array.
[
  {
    "href": "http://xxxxxx:8081/analytics/uves/vrouter/devstack1?flat",
    "name": "devstack1"
  }
]
3.process href and query again
4.VrouterAgent.vr_limits.vrouter_build_info
5.VrouterAgent.build_info

1.Query contraolnode endpoint
2.Get the list of controlnodes in array.

[
  {
    "href": "http://xxxxx:8081/analytics/uves/control-node/opencontrail?flat",
    "name": "opencontrail"
  }
]
3.process href and query again
4.BgpRouterState.build_info":
"""

import sys
import argparse
import logging
import json
import os
import requests

VROUTER_API = "vrouters"
CONTROL_API = "control-nodes"
CONFIG_API = "config-nodes"
ANALYTICS_API = "analytics-nodes"
DNS_API = "dns-nodes"
UVEAPI = "analytics/uves/"


def control_version(analytics_ip):
    result = []
    ANALYTICS_NODE = "http://" + analytics_ip + ":8081/"
    URI = ANALYTICS_NODE + UVEAPI + CONTROL_API
    resp = requests.get(URI)
    if resp.status_code != 200:
        print "something wrong in API...exiting"
        return
    for cnapi in resp.json():
        resp1 = requests.get(cnapi["href"])
        cndata = resp1.json()
        node = cndata["BgpRouterState"]
        result.append({
            "control-node": node["build_info"]
            })
    return result

def dns_version(analytics_ip):
    result = []
    ANALYTICS_NODE = "http://" + analytics_ip + ":8081/"
    URI = ANALYTICS_NODE + UVEAPI + DNS_API
    resp = requests.get(URI)
    if resp.status_code != 200:
        print "something wrong in API...exiting"
        return
    for dnapi in resp.json():
        resp1 = requests.get(dnapi["href"])
        dndata = resp1.json()
        node = dndata["DnsState"]
        result.append({
            "dns-node": node["build_info"]
            })
    return result

def config_version(analytics_ip):
    result = []
    ANALYTICS_NODE = "http://" + analytics_ip + ":8081/"
    URI = ANALYTICS_NODE + UVEAPI + CONFIG_API
    resp = requests.get(URI)
    if resp.status_code != 200:
        print "something wrong in API...exiting"
        return
    for cfapi in resp.json():
        resp1 = requests.get(cfapi["href"])
        cfdata = resp1.json()
        node = cfdata["ModuleCpuState"]
        result.append({
            "config-node": node["build_info"]
            })
    return result


def analytics_version(analytics_ip):
    result = []
    ANALYTICS_NODE = "http://" + analytics_ip + ":8081/"
    URI = ANALYTICS_NODE + UVEAPI + ANALYTICS_API
    resp = requests.get(URI)
    if resp.status_code != 200:
        print "something wrong in API...exiting"
        return
    for anapi in resp.json():
        resp1 = requests.get(anapi["href"])
        andata = resp1.json()
        node = andata["CollectorState"]
        result.append({
            "analytics-node": node["build_info"]
            })
    return result


def vouter_version(analytics_ip):
    result = []
    ANALYTICS_NODE = "http://" + analytics_ip + ":8081/"
    URI = ANALYTICS_NODE + UVEAPI + VROUTER_API
    resp = requests.get(URI)
    if resp.status_code != 200:
        print "something wrong in API...exiting"
        return
    for vrapi in resp.json():
        resp1 = requests.get(vrapi["href"])
        vrdata = resp1.json()
        vr_agent = vrdata["VrouterAgent"]
        result.append({
            "vrouter-agent": vr_agent["build_info"],
            "vrouter": vr_agent["vr_limits"]["vrouter_build_info"]
            })
    return result


def process_args(argv):
    parser = argparse.ArgumentParser("contrail version collector Script ")
    parser.add_argument("-I", "--analytics-ip",  help="Analytics node IP, no PORT required", required=True)
    options = parser.parse_args()
    return options


def main(argv):
    """Main routine."""
    options = process_args(argv)
    logging.info('Contrail Version collector script starts with the arguments %s' % options)
    print vouter_version(options.analytics_ip)
    print control_version(options.analytics_ip)
    print config_version(options.analytics_ip)
    print analytics_version(options.analytics_ip)
    print dns_version(options.analytics_ip)

if __name__ == "__main__":
    main(sys.argv)
