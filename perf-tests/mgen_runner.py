import os
import sys
#import psutil
import argparse
from threading import Timer
from time import sleep
import time
"""
python mgen-client.py -- server-ip 10.0.1.3 --server-port 5000  --duration 600 --pkt-size 64 \
      --connections 1000  --connections-step 1000

python mgen-server.py  --server-port 5000  --duration 500

"""

def writefile(filename, data):
    file = open(filename, "a")
    file.write(data)
    file.write("\n")
    file.close()


def write_mgen_file(args):
    # 0.0 ON 1 UDP DST 10.24.0.3/5001 PERIODIC [1000 1240]
    # 60.0OFF 1
    for i in range(1, int(args.flows)):
        d = "0.0 ON "+ str(i) + " UDP DST " + str(args.server_ip) + "/" + str(args.server_port) + " PERIODIC ["+ str(args.pkt_size)+ " "+ str(args.pkts_per_sec)+ "] " 
        writefile("ip.mgen",d)
    for i in range(1, int(args.flows)):
        d =  str(args.duration) + ".0 0FF " + str(i)
        writefile("ip.mgen",d)




def main(argv):
    parser = argparse.ArgumentParser("Program for measuring the memory,cpu")
    parser.add_argument("--server-ip", required=True, help="Input Server IP")
    parser.add_argument("--server-port", required=True, help="Server Port")
    parser.add_argument("--duration", required=True, help="Measure Duration")
    parser.add_argument("--pkt-size", required=False, default=100, help="Packet Size")
    parser.add_argument("--pkts-per-sec", required=False, default=1, help="Packet Size")
    parser.add_argument("--flows", required=True, help="connections Size")
    parser.add_argument("--flows-increase-step", required=False, help="connections Step")
    args = parser.parse_args(argv[1:])
    print args
    write_mgen_file(args)


if __name__ == '__main__':
    main(sys.argv)