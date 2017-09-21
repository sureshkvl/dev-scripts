import sys
import argparse
import logging
import json
import os
import requests
import time
#import xlsxwriter


VROUTER_API = "vrouters"
ANALYTICS_API = "analytics-nodes"
UVEAPI = "analytics/uves/"

logging.basicConfig(stream=sys.stdout, filename='vrouter_stats.log',level=logging.INFO)


"""
prev_inbytes = 0
prev_outbytes = 0
curr_inbytes = 0
curr_outbytes = 0
prev_inpkts = 0
prev_outpkts = 0
"""

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
    "FR_active_flows"
    "FR_max_flow_deletes_per_second"
    "FR_added_flows"
    "FR_deleted_flows"
    "FR_min_flow_adds_per_second"
    "FR_min_flow_deletes_per_second"
    "FR_max_flow_adds_per_second"
    "ds_rewrite_fail": 0,
            "ds_mcast_df_bit": 0,
            "ds_flow_no_memory": 0,
            "ds_push": 0,
            "ds_invalid_if": 9,
            "ds_pull": 3,
            "ds_no_fmd": 0,
            "ds_invalid_arp": 0,
            "ds_trap_no_if": 0,
            "ds_cksum_err": 13,
            "ds_invalid_source": 117,
            "ds_flow_action_invalid": 0,
            "ds_invalid_packet": 0,
            "ds_flow_invalid_protocol": 0,
            "ds_invalid_vnid": 0,
            "ds_flow_table_full": 0,
            "ds_invalid_label": 0,
            "ds_garp_from_vm": 0,
            "ds_frag_err": 0,
            "ds_duplicated": 1170509,
            "ds_clone_fail": 0,
            "ds_arp_no_route": 0,
            "ds_misc": 1302,
            "ds_flood": 0,
            "ds_interface_rx_discard": 0,
            "ds_flow_unusable": 0,
            "ds_mcast_clone_fail": 0,
            "ds_invalid_protocol": 0,
            "ds_head_space_reserve_fail": 0,
            "ds_interface_tx_discard": 10,
            "ds_flow_action_drop": 29928,
            "ds_nowhere_to_go": 0,
            "ds_cloned_original": 137731,
            "ds_l2_no_route": 1606,
            "ds_invalid_mcast_source": 0,
            "ds_discard": 0,
            "ds_flow_queue_limit_exceeded": 9018,
            "ds_flow_nat_no_rflow": 0,
            "ds_invalid_nh": 144,
            "ds_head_alloc_fail": 0,
            "ds_interface_drop": 0,
            "ds_pcow_fail": 0,
            "ds_ttl_exceeded": 0
}


report = {
    "Time": None,
    "InPackets": 0
    "OutPackets": 0
    "InBytes": 0
    "OutBytes": 0
    "Exception Packets":0
    "InBandwidth":0
    "OutBandwidth":0
    "CPU Utils":
    "Memory Utils":
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
        in_memory_db[key] = [0, 0, 0, 0]
        return in_memory_db[key]

def get_vrouter_name(url):
    #http://10.0.1.3:8081/analytics/uves/vrouter/contraildev?flat
    res = url.split("/")    
    return res[len(res)-1]
"""
#Excel file
workbook = None
worksheet = None
row = 1
def create_excel(fname, header):
    global workbook
    global worksheet
    global row
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(fname)
    worksheet = workbook.add_worksheet()

def close_excel():
    workbook.close()

def write_excel_file(data):
    global workbook
    global worksheet
    global row
    col = 0
    for val in data:
        worksheet.write(row, col, val)
        col += 1
    row += 1
"""

#Plain CSV file
def writefile(filename, data):
    file = open(filename, "a")
    file.write(data + "\n")
    file.close()

def write_csv_file(filename, data):
    writefile(filename, ','.join(data))


def write_data(name, data):
    res = [str(data["Time"]), str(data["InPackets"]), str(data["OutPackets"]), str(data["InBandwidth"]),
            str(data["OutBandwidth"]), str(data["ExceptionPkts"]), str(data["TotalMem"]),
            str(data["FreeMem"]), str(data["CPULoadAvg"]), str(data["FR_active_flows"]),
            str(data["FR_added_flows"]), str(data["FR_min_flow_adds_per_second"]),
            str(data["FR_max_flow_adds_per_second"]),str(data["FR_deleted_flows"]),
            str(data["FR_min_flow_deletes_per_second"]),str(data["FR_max_flow_deletes_per_second"]),
            str(data["ds_flow_no_memory"]),
            str(data["ds_flow_action_invalid"]), str(data["ds_flow_invalid_protocol"]),
            str(data["ds_flow_table_full"]), str(data["ds_flow_unusable"]),
            str(data["ds_flow_action_drop"]), str(data["ds_flow_queue_limit_exceeded"]),
            str(data["ds_flow_nat_no_rflow"])
           ]
    write_csv_file(name + ".csv", res)
    #write_excel_file(res)

def write_header(name):
    hdr = ["Time", "InPackets", "OutPackets", "InBandwidth", "OutBandwidth", "ExceptionPkts",
           "TotalMem", "FreeMem", "CPULoadAvg", "FR_active_flows",
           "FR_added_flows", "FR_min_flow_adds_per_second", "FR_max_flow_adds_per_second",
           "FR_deleted_flows","FR_min_flow_deletes_per_second","FR_max_flow_deletes_per_second",
           "ds_flow_no_memory", "ds_flow_action_invalid", "ds_flow_invalid_protocol", 
           "ds_flow_table_full", "ds_flow_unusable", "ds_flow_action_drop", "ds_flow_queue_limit_exceeded",
           "ds_flow_nat_no_rflow"
           ]
    write_csv_file(name + ".csv", hdr)
    #create_excel(name + ".xls")
    #write_excel_file(hdr)


def vrouter_stats(vrouters, inter, t):
    for vrouter in vrouters:
        val = get_kv(vrouter["vrouter-name"])
        # packet, bytes, bandwidth calculation
        prev_inbytes = val[0]
        prev_outbytes = val[1]
        prev_inpkts = val[2]
        prev_outpkts = val[3]
        if prev_inbytes == 0:
            prev_inbytes = vrouter['data']['in_bytes']
        if prev_outbytes == 0:
            prev_outbytes = vrouter['data']['out_bytes']
        if prev_inpkts == 0:
            prev_inpkts = vrouter['data']['in_tpkts']
        if prev_outpkts == 0:
            prev_outpkts = vrouter['data']['out_tpkts']

        curr_inbytes = vrouter['data']['in_bytes']
        curr_outbytes = vrouter['data']['out_bytes']
        curr_inpkts = vrouter['data']['in_tpkts']
        curr_outtpkts = vrouter['data']['out_tpkts']

        InPkts = curr_inpkts - prev_inpkts
        OutPkts = curr_outtpkts - prev_outpkts
        InMbps = ((curr_inbytes - prev_inbytes) * 8) / (1000000 * inter)
        OutMbps = ((curr_outbytes - prev_outbytes) * 8) / (1000000 * inter)
        prev_inbytes = curr_inbytes
        prev_outbytes = curr_outbytes
        prev_inpkts = curr_inpkts
        prev_outpkts = curr_outtpkts
        update_kv(vrouter["vrouter-name"], [prev_inbytes, prev_outbytes, prev_inpkts, prev_outpkts])

        drop_stats = {}
        if vrouter["data"].has_key("drop_stats"):
            drop_stats = {
                "ds_flow_no_memory": vrouter['data']['drop_stats']["ds_flow_no_memory"],
                "ds_flow_action_invalid": vrouter['data']['drop_stats']["ds_flow_action_invalid"],
                "ds_flow_invalid_protocol": vrouter['data']['drop_stats']["ds_flow_invalid_protocol"],
                "ds_flow_table_full": vrouter['data']['drop_stats']["ds_flow_table_full"],
                "ds_flow_unusable": vrouter['data']['drop_stats']["ds_flow_unusable"],
                "ds_flow_action_drop": vrouter['data']['drop_stats']["ds_flow_action_drop"],
                "ds_flow_queue_limit_exceeded": vrouter['data']['drop_stats']["ds_flow_queue_limit_exceeded"],
                "ds_flow_nat_no_rflow": vrouter['data']['drop_stats']["ds_flow_nat_no_rflow"]
                }
        else:
            drop_stats = {
                "ds_flow_no_memory": -1,
                "ds_flow_action_invalid": -1,
                "ds_flow_invalid_protocol": -1,
                "ds_flow_table_full": -1,
                "ds_flow_unusable": -1,
                "ds_flow_action_drop": -1,
                "ds_flow_queue_limit_exceeded": -1,
                "ds_flow_nat_no_rflow": -1
                }
        flow_stats = {}
        if vrouter["data"].has_key("flow_rate"):
            flow_stats = {
            "FR_active_flows": vrouter['data']['flow_rate']["active_flows"],
            "FR_max_flow_deletes_per_second": vrouter['data']['flow_rate']["max_flow_deletes_per_second"],
            "FR_added_flows": vrouter['data']['flow_rate']["added_flows"],
            "FR_deleted_flows": vrouter['data']['flow_rate']["deleted_flows"],
            "FR_min_flow_adds_per_second": vrouter['data']['flow_rate']["min_flow_adds_per_second"],
            "FR_min_flow_deletes_per_second": vrouter['data']['flow_rate']["min_flow_deletes_per_second"],
            "FR_max_flow_adds_per_second": vrouter['data']['flow_rate']["max_flow_adds_per_second"]
            }
        else:
            flow_stats = {
                "FR_active_flows": -1,
                "FR_max_flow_deletes_per_second": -1,
                "FR_added_flows": -1,
                "FR_deleted_flows": -1,
                "FR_min_flow_adds_per_second": -1,
                "FR_min_flow_deletes_per_second": -1,
                "FR_max_flow_adds_per_second": -1
            }

        result =   {
            "Time": time.ctime(t),
            "InPackets": (InPkts/inter),
            "OutPackets": (OutPkts/inter),
            "InBandwidth": InMbps,
            "OutBandwidth": OutMbps,
            "ExceptionPkts": vrouter['data']['exception_packets'],
            "TotalMem": vrouter['data']['cpu_info']['sys_mem_info']['total'],
            "FreeMem": vrouter['data']['cpu_info']['sys_mem_info']['free'],
            "CPULoadAvg": vrouter['data']['cpu_info']['cpuload']['one_min_avg']
            }

        result.update(drop_stats)
        result.update(flow_stats)
        write_data(vrouter["vrouter-name"],result )

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
            write_header(get_vrouter_name(vrapi["href"]))

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
    parser.add_argument("-D", "--duration",  help="duration of run(seconds)", required=False, default=600)
    options = parser.parse_args()
    return options

def main(argv):
    """Main routine."""
    options = process_args(argv)
    poll_interval = 30
    logging.info('Contrail Vrouter Stats script starts with the arguments %s' % options)
    for i in range(0, (int(options.duration) / poll_interval)+1):
        t = time.time()
        logging.info('Time %s' % time.ctime(t))
        x = vouter_uves(options.analytics_ip)
        logging.info("Vrouter Statistics Dump : %s" % x)
        vrouter_stats(x, poll_interval, t)
        time.sleep(poll_interval)


if __name__ == "__main__":
    main(sys.argv)
