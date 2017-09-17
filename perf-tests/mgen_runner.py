import os
import sys
import argparse
from threading import Timer
from time import sleep
import time
import subprocess
"""
python mgen-client.py -- server-ip 10.0.1.3 --server-port 5000  --duration 600 --pkt-size 64 \
      --connections 1000  --connections-step 1000

python mgen-server.py  --server-port 5000  --duration 500

"""
FLOWS_PER_PROCESS = 500
FLOW_NO = 1
SRC_PORT_NO = 1000


def process_mgen_output():
    pass

def run_mgen_test(filenames):
    #mgen input input.mgen txlog output outputtx.log
    for fname in filenames:
        #retcode = subprocess.call(["mgen", "input", fname,  "&"])
        p1 = subprocess.Popen(["mgen", "input", fname, "nolog"])
        print p1
    return

def writefile(filename, data):
    file = open(filename, "a")
    file.write(data)
    file.write("\n")
    file.close()

def write_mgen_file(args, fname, flowseqno, srcportno, totalflows, flowpersec):
    # 0.0 ON 1 UDP SRC 5001  DST 10.24.0.3/5001 PERIODIC [1000 1240]
    # 60.0OFF 1
    iteration = int(totalflows) / int(flowpersec)
    flowno = flowseqno
    for i in range(0, iteration):
        for f in range (0, int(flowpersec)):
            d = str(i) + ".0 ON "+ str(flowno) + " UDP SRC " + str(srcportno) + " DST " + str(args.server_ip) + "/" + str(args.server_port) + " PERIODIC ["+ str(args.pkts_per_sec)+ " "+ str(args.pkt_size)+ "] " 
            flowno = flowno+1
            srcportno = srcportno + 1
            # print d
            writefile(fname, d)

    for i in range(flowseqno, flowno):
        d =  str(args.duration) + ".0 OFF " + str(i)
        # print d
        writefile(fname, d)



"""
def write_mgen_file(args):
    # clean up the exisitng files
    os.remove(fname)
    os.remove(oname)
    # 0.0 ON 1 UDP SRC 5001  DST 10.24.0.3/5001 PERIODIC [1000 1240]
    # 60.0OFF 1
    flowno = 1
    portno = 1000
    for i in range(0, int(args.flows)):
        d = "0.0 ON "+ str(flowno) + " UDP SRC " + str(portno+flowno) +" DST " + str(args.server_ip) + "/" + str(args.server_port) + " PERIODIC ["+ str(args.pkts_per_sec)+ " "+ str(args.pkt_size)+ "] " 
        writefile(fname,d)
        flowno = flowno + 1
    
    if args.flows_increase_step:
        for i in range(1, int(args.duration)):
            for f in range(0, int(args.flows_increase_step)):
                d = str(i) + ".0 ON "+ str(flowno) + " UDP SRC " + str(portno+flowno) +" DST " + str(args.server_ip) + "/" + str(args.server_port) + " PERIODIC ["+ str(args.pkts_per_sec) + " "+ str(args.pkt_size)+ "] " 
                writefile(fname,d)
                flowno = flowno + 1

    for i in range(1, flowno):
        d =  str(args.duration) + ".0 OFF " + str(i)
        writefile(fname, d)
"""



def main(argv):
    parser = argparse.ArgumentParser("Program for measuring the memory,cpu")
    parser.add_argument("--server-ip", required=True, help="Input Server IP")
    parser.add_argument("--server-port", required=True, help="Server Port")
    parser.add_argument("--duration", required=True, help="Measure Duration")
    parser.add_argument("--pkt-size", required=False, default=64, help="Packet Size")
    parser.add_argument("--pkts-per-sec", required=False, default=1, help="Packet Size")
    #parser.add_argument("--flows", required=True, help="connections Size")
    #parser.add_argument("--flows-increase-step", required=False, help="connections Step")
    parser.add_argument("--total-flows", required=True, help="connections Size")
    parser.add_argument("--flows-per-sec", required=False, help="connections Step")
    args = parser.parse_args(argv[1:])
    print args
    filenames = []
    if int(args.total_flows) <= FLOWS_PER_PROCESS:
        filename = "input0.mgen"
        filenames.append(filename)
        write_mgen_file(args, filename, FLOW_NO, SRC_PORT_NO, args.total_flows, args.flows_per_sec )
    else:
        q = int(args.total_flows) / FLOWS_PER_PROCESS
        r = int(args.total_flows) % FLOWS_PER_PROCESS

        current_flow_no = FLOW_NO
        current_src_port_no = SRC_PORT_NO

        for p in range(0, q):
            filename = "input" + str(p) +".mgen"
            filenames.append(filename)
            write_mgen_file(args, filename, current_flow_no, current_src_port_no, FLOWS_PER_PROCESS, int(args.flows_per_sec)/q )
            current_flow_no = current_flow_no + FLOWS_PER_PROCESS
            current_src_port_no = current_src_port_no + FLOWS_PER_PROCESS
        print filenames
    run_mgen_test(filenames)
    #process_mgen_output()

if __name__ == '__main__':
    main(sys.argv)
