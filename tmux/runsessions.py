import sys
import argparse
import logging
import json
import os
# cmd = 'ls -al'
# os.system(cmd)
logging.basicConfig(level=logging.DEBUG)


def run(op):
    tmux = op["tmux"]
    cmd = "tmux new-session -s "+ tmux["session_name"] + " -d"
    logging.info('Creating new TMUX Session -  %s' % cmd)
    os.system(cmd)
    windows = tmux["windows"]
    i = 1
    for window in windows:
        session = tmux["session_name"] + ":" + str(i)
        cmd1 = "tmux new-window -t "+ session + " -n  " + window["name"]
        logging.info('Creating new TMUX Window -  %s' % cmd1)
        os.system(cmd1)
        cmd2 = "tmux send-keys -t " + session + " " + window["execute"] + " C-m"
        logging.info('Executing Command in the TMUX Window -  %s' % cmd2)
        os.system(cmd2)
        i = i+1
    logging.info("TMUX Session creation Completed\n")
    cmd = "tmux attach-session -t " + tmux["session_name"]
    logging.info(" To Attach to this running session, use this command -  %s " %cmd)
    cmd = "tmux kill-session -t " + tmux["session_name"]
    logging.info(" To Kill this  session, use this command -  %s " %cmd )





def read_and_validate(fname):
    with open(fname) as json_file:
        json_data = json.load(json_file)
        logging.info("JSON  is : %s" % json_data)
        return json_data

def t_print(op):
    tmux = op["tmux"]
    print tmux.get("session_name")
    print tmux.get("windows")

def validate_json(op):
    tmux = op["tmux"]
    print tmux.get("session_name")
    print tmux.get("windows")


def process_args(argv):
    parser = argparse.ArgumentParser("TMUX automation Script ")
    parser.add_argument("-I", "--input-file",  help="Input Job file name in JSON format", required=True)
    options = parser.parse_args()
    return options


def main(argv):
    """Main routine."""
    options = process_args(argv)
    logging.info('TMUX Automation script starts with the arguments %s' % options)
    op = read_and_validate(options.input_file)
    t_print(op)
    run(op)

if __name__ == "__main__":
    main(sys.argv)
