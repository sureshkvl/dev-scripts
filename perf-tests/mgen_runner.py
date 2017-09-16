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
fname = "input.mgen"
oname = "outputtx.log"
def process_mgen_output():
    pass

def run_mgen_test():
    #mgen input input.mgen txlog output outputtx.log
    retcode = subprocess.call(["mgen", "input", fname, "txlog", "output", oname])
    print retcode
    return

def writefile(filename, data):
    file = open(filename, "a")
    file.write(data)
    file.write("\n")
    file.close()

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

def main(argv):
    parser = argparse.ArgumentParser("Program for measuring the memory,cpu")
    parser.add_argument("--server-ip", required=True, help="Input Server IP")
    parser.add_argument("--server-port", required=True, help="Server Port")
    parser.add_argument("--duration", required=True, help="Measure Duration")
    parser.add_argument("--pkt-size", required=False, default=64, help="Packet Size")
    parser.add_argument("--pkts-per-sec", required=False, default=1, help="Packet Size")
    parser.add_argument("--flows", required=True, help="connections Size")
    parser.add_argument("--flows-increase-step", required=False, help="connections Step")
    args = parser.parse_args(argv[1:])
    print args
    write_mgen_file(args)
    run_mgen_test()
    process_mgen_output()

if __name__ == '__main__':
    main(sys.argv)
