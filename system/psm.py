import os
import sys
#import psutil
import argparse
from threading import Timer
from time import sleep
import time

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


def writefile(filename, data):
    file = open(filename, "a")
    file.write(data)
    file.write("\n")
    file.close()


def pid_measure(pids, ):
    if not pids:
        return
    Result = []
    for pid in pids:
        res = [pid]
        try:
            p = psutil.Process(int(pid))
            localtime = time.asctime(time.localtime(time.time()))
            res.append(localtime)
            res.append(p.memory_percent())
            res.append(p.cpu_percent(interval=1.0))
        except:
            print "ERROR: while reading the process,memory"
            sys.exit()
        finally:
            Result.append(res)
    writefile("processutilization.result", str(Result))

def cpu_measure(i):
    Result = []
    res = []
    try:
        localtime = time.asctime(time.localtime(time.time()))
        p = psutil.cpu_percent(interval=i, percpu=True)
        res.append(localtime)
        res.append(p)
        res.append(psutil.virtual_memory())
    except:
        print "ERROR: while reading the process,memory"
    finally:
        Result.append(res)
    writefile("cpuutilization.result", str(Result))


def cpu_measure2():
    localtime = time.asctime(time.localtime(time.time()))
    tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1].split()[1:])
    # print "Total Mem", tot_m
    # print "Used Mem", used_m
    # print "Free Mem",free_m

    nproc = os.popen('nproc').readlines()[-1].split()[0]
    #nproc.rstrip()
    # print "Number of CPU cores", nproc

    onemin, fivemin, tenmin, num_p, l_pid = map(str, os.popen('cat /proc/loadavg').readlines()[-1].split()[0:])
    # print onemin
    # print fivemin
    # print tenmin
    res = str(localtime) + "   " + str(tot_m) + "   " + str(used_m) + "   " + str(free_m) + "   " + str(nproc) + "       " + str(onemin) + "     " + str(fivemin) + "      " + str(tenmin)
    writefile("cpumeasure.result", res)



def main(argv):
    parser = argparse.ArgumentParser("Program for measuring the memory,cpu")
    parser.add_argument("-p", "--pid", required=False,
                        help="Input PID Number", action="append")
    parser.add_argument("-i", "--interval", required=False, default=30,
                        help="Measure Interval")
    parser.add_argument("-d", "--duration", required=False, default=3600,
                        help="Measure Duration")

    args = parser.parse_args(argv[1:])
    print args
    if args.pid:
        pid_rt = RepeatedTimer(args.interval, pid_measure, args.pid)
    sys_rt = RepeatedTimer(args.interval, cpu_measure2)
    hdr = "Time                 Tot_M   Used_M  Free_M   Num_P  1minLoad   5minLoad  10minLoad"
    writefile("cpumeasure.result", hdr)


    try:
        sleep(args.duration)
    finally:
        sys_rt.stop()
        if args.pid:
            pid_rt.stop()

if __name__ == '__main__':
    main(sys.argv)
