
import sys
import argparse
import logging
import json
import os
import requests
import time

VROUTER_API = "vrouters"
CONTROL_API = "control-nodes"
CONFIG_API = "config-nodes"
ANALYTICS_API = "analytics-nodes"
DNS_API = "dns-nodes"
UVEAPI = "analytics/uves/"

logging.basicConfig(stream=sys.stdout, filename='vrouter_stats.log',level=logging.INFO)


prev_inbytes = 0
prev_outbytes = 0
curr_inbytes = 0
curr_outbytes = 0
Measure_Interval = 0


def phy_stats():
    pass


def cpu_stats(vrouters):
    for vrouter in vrouters:
        logging.info('CPU Stats ')
        logging.info('cpu_info  %s ' % vrouter['cpu_info'])


def vhost_stats(vrouters):
    for vrouter in vrouters:
        logging.info('Vrouter Vhost Stats ')
        logging.info(" Uptime  %s" % vrouter['uptime'])
        logging.info(" in_pkts  %s" % vrouter['vhost_stats']['in_pkts'])
        logging.info(" out_pkts  %s" % vrouter['vhost_stats']['out_pkts'])
        logging.info(" in_bytes  %s" % vrouter['vhost_stats']['in_bytes'])
        logging.info(" out_bytes  %s" % vrouter['vhost_stats']['out_bytes'])
        logging.info(" drop_stats  %s" % vrouter['vhost_drop_stats'])

def vrouter_stats(vrouters):
    logging.info(" MEasure Interval  %s" % Measure_Interval)
    for vrouter in vrouters:
        logging.info('Vrouter Stats ')
        if prev_inbytes == 0:
            prev_inbytes = vrouter['in_tpkts']
        if prev_outbytes == 0:
            prev_outbytes = vrouter['out_tpkts']

        curr_inbytes = vrouter['in_tpkts']
        curr_outbytes = vrouter['out_tpkts']
        InMbps = curr_inbytes - prev_inbytes * 8 / (1000000 * Measure_Interval)
        OutMbps = curr_outbytes - prev_outbytes * 8 / (1000000 * Measure_Interval)

        logging.info(" in_pkts  %s" % vrouter['in_tpkts'])
        logging.info(" out_pkts  %s" % vrouter['out_tpkts'])
        logging.info(" exception_pkts  %s" % vrouter['exception_packets'])
        logging.info(" in_bytes  %s" % vrouter['in_bytes'])
        logging.info(" out_bytes  %s" % vrouter['out_bytes'])
        logging.info(" InMpbs  %s" % InMbps)
        logging.info(" OutMpbs  %s" % OutMbps)
        logging.info(" drop_stats  %s" % vrouter['drop_stats']['ds_drop_pkts'])
        #logging.info(" drop_stats  %s" % vrouter['drop_stats'])

def vouter_uves(analytics_ip):
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
        vr_agent = vrdata["VrouterStatsAgent"]
        result.append(vr_agent)
    return result

def process_args(argv):
    parser = argparse.ArgumentParser("contrail Vrouter Stats script ")
    parser.add_argument("-I", "--analytics-ip",  help="Analytics node IP, no PORT required", required=True)
    parser.add_argument("-P", "--poll-interval", type=int, default=30, help="Poll Interval in sec", required=True)    
    options = parser.parse_args()
    return options

def main(argv):
    """Main routine."""
    options = process_args(argv)
    logging.info('Contrail Vrouter Stats script starts with the arguments %s' % options)
    while(1):
        t = time.time()
        logging.info('Time %s' % t)
        logging.info('Time %s' % time.ctime(t))
        x = vouter_uves(options.analytics_ip)
        vrouter_stats(x)
        #vhost_stats(x)
        #cpu_stats(x)
        time.sleep(options.poll_interval)

if __name__ == "__main__":
    main(sys.argv)


# vrouter-stats.py -I analytics-ip
#
#
