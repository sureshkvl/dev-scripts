import sys
import argparse
import logging
import os
import requests
from datetime import datetime
import time
#from pyping import pyping
from pyping import ping, Ping

logging.basicConfig(stream=sys.stdout, filename='monitor.log',level=logging.INFO)


def http_checker(args):
    Msgs = ""
    for arg in args:
        URI = "http://" + arg + ":80"
        Msg = str(datetime.now()) + "\tHTTP\t" + URI + "\t"
        try:
            resp = requests.get(URI, timeout=5)
            Msg += str(resp.status_code)
            if resp.status_code != 200:
                Msg += "\tNot Reachable\t"
            else:
                Msg += "\tReachable\t"
        except:
            Msg += str(sys.exc_info()[0])
        Msg += "\n"
        Msgs += Msg
    return Msgs   

def ping_checker(args):
    Msg = ""
    for arg in args:
        r = ping(arg, count=1, timeout=3000, udp=False)
        Msg  += str(datetime.now()) + "\tPING\t" + arg + "\t"+ "Pktloss:"+str(r.packet_lost)+ "\t" + "RTT:" + str(r.avg_rtt)
        Msg  += "\n"
    return Msg

def process_args(argv):
    parser = argparse.ArgumentParser("Monitor Script ")
    parser.add_argument("-H", "--http_ip",  help="HTTP IP for monitoring", required=False, action='append')
    parser.add_argument("-P", "--ping_ip",  help="PING IP for monitoring", required=True, action='append')
    options = parser.parse_args()
    return options


def main(argv):
    """Main routine."""
    options = process_args(argv)
    logging.info('Monitor starts with the arguments %s' % options)
    #print "Monitor starts with the arguments ", options
    while (1):
        logging.info(ping_checker(options.ping_ip))
        logging.info(http_checker(options.http_ip))
        time.sleep(1)

if __name__ == "__main__":
    main(sys.argv)

