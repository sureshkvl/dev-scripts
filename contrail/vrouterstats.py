import sys
import argparse
import logging
import json
import os
import requests
import time

VROUTER_API = "vrouters"
ANALYTICS_API = "analytics-nodes"
UVEAPI = "analytics/uves/"

logging.basicConfig(stream=sys.stdout, filename='vrouter_stats.log',level=logging.INFO)

prev_inbytes = 0
prev_outbytes = 0
curr_inbytes = 0
curr_outbytes = 0

"""
report = {
    "Time": None,
    "Ingress-BW(Mbps)": None,
    "Egress-BW(Mbps)": None,
    "Exception Pkts": None,
    "Dropped Pkts": None,
    "Total Mem": None,
    "Free Mem": None,
    "CPU Load AVG(1min)": None
}
"""

in_memory_db = {}
def update_kv(key, value):
    global in_memory_db
    in_memory_db[key] = value

def get_kv(key):
    global in_memory_db
    if in_memory_db.has_key(key):
        return in_memory_db[key]
    else:
        in_memory_db[key] = [0, 0]
        return in_memory_db[key]

def get_vrouter_name(url):
    #http://10.0.1.3:8081/analytics/uves/vrouter/contraildev?flat
    res = url.split("/")    
    return res[len(res)-1]

def writefile(filename, data):
    file = open(filename, "a")
    file.write(data)
    file.close()

def write_header(filename):
    tmp = ["Time","Ingress-BW(Mbps)","Egress-BW(Mbps)","Exception Pkts","Dropped Pkts","Total Mem","Free Mem","CPU Load AVG(1min)"]
    header = '\t'.join(tmp)
    writefile(filename, header)

def write_data(filename, result):
    tmp = result.values()
    res = result["Time"] + "\t" + str(result["Ingress-BW(Mbps)"]) + "\t" + str(result["Egress-BW(Mbps)"]) + "\t"
    res = res + str(result["Exception Pkts"]) + "\t" + str(result["Dropped Pkts"]) + "\t"
    res = res + str(result["Total Mem"]) + "\t" + str(result["Free Mem"]) + "\t" + str(result["CPU Load AVG(1min)"]) + "\n"
    writefile(filename, res)

"""
def cpu_stats(vrouters):
    for vrouter in vrouters:
        logging.info('CPU Stats ')
        logging.info('cpu_info  %s ' % vrouter['cpu_info'])
"""

def vrouter_stats(vrouters, inter, t):
    #"vrouter-name"
    #global prev_inbytes
    #global prev_outbytes
    for vrouter in vrouters:
        val = get_kv(vrouter["vrouter-name"])
        prev_inbytes = val[0]
        prev_outbytes = val[1]
        if prev_inbytes == 0:
            prev_inbytes = vrouter['data']['in_bytes']
        if prev_outbytes == 0:
            prev_outbytes = vrouter['data']['out_bytes']

        curr_inbytes = vrouter['data']['in_bytes']
        curr_outbytes = vrouter['data']['out_bytes']
        InMbps = ((curr_inbytes - prev_inbytes) * 8) / (1000000 * inter)
        OutMbps = ((curr_outbytes - prev_outbytes) * 8) / (1000000 * inter)
        prev_inbytes = curr_inbytes
        prev_outbytes = curr_outbytes
        update_kv(vrouter["vrouter-name"], [prev_inbytes,prev_outbytes])

        write_data(vrouter["vrouter-name"]+".result",
            {
            "Time": time.ctime(t),
            "Ingress-BW(Mbps)": InMbps,
            "Egress-BW(Mbps)": OutMbps,
            "Exception Pkts": vrouter['data']['exception_packets'],
            "Dropped Pkts": vrouter['data']['drop_stats']['ds_drop_pkts'],
            "Total Mem": vrouter['data']['cpu_info']['sys_mem_info']['total'],
            "Free Mem": vrouter['data']['cpu_info']['sys_mem_info']['free'],
            "CPU Load AVG(1min)": vrouter['data']['cpu_info']['cpuload']['one_min_avg']
            })

header_written = 0
def vouter_uves(analytics_ip):
    result = []
    ANALYTICS_NODE = "http://" + analytics_ip + ":8081/"
    URI = ANALYTICS_NODE + UVEAPI + VROUTER_API
    resp = requests.get(URI)
    if resp.status_code != 200:
        print "something wrong in API...exiting"
        return
    global header_written
    if header_written == 0:
        header_written = 1
        for vrapi in resp.json():
            write_header(get_vrouter_name(vrapi["href"])+".result")

    for vrapi in resp.json():
        resp1 = requests.get(vrapi["href"])
        logging.info(" HTTP Req to %s" % vrapi["href"])
        vrdata = resp1.json()
        vr_agent = vrdata["VrouterStatsAgent"]
        result.append({"vrouter-name": get_vrouter_name(vrapi["href"]), "data": vr_agent})
    return result

def process_args(argv):
    parser = argparse.ArgumentParser("contrail Vrouter Stats script ")
    parser.add_argument("-I", "--analytics-ip",  help="Analytics node IP, no PORT required", required=True)
    #parser.add_argument("-P", "--poll-interval", type=int, default=30, help="Poll Interval in sec", required=True)    
    options = parser.parse_args()
    return options

def main(argv):
    """Main routine."""
    options = process_args(argv)
    poll_interval = 30
    logging.info('Contrail Vrouter Stats script starts with the arguments %s' % options)
    while(1):
        t = time.time()
        logging.info('Time %s' % time.ctime(t))
        x = vouter_uves(options.analytics_ip)
        logging.info("Vrouter Statistics Dump : %s" % x)
        vrouter_stats(x, poll_interval, t)
        time.sleep(poll_interval)

if __name__ == "__main__":
    main(sys.argv)

# vrouter-stats.py -I analytics-ip
#
#
