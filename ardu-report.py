#!/usr/bin/env python

"""
PURPOSE:      read the serial output of one or more arduino boards
              and store the sensor values..
DEPENDENCY:   python 2.7, see requirements.txt
PLATTFORM:    currently only unix/linux is supported
AUTHOR(S):    michael lustenberger inofix.ch
COPYRIGHT:    (C) 2017 by Michael Lustenberger and INOFIX GmbH

              This program is free software under the GNU General Public
              License (>=v2).
"""

#from libardurep import datastore, datareporter, serialreader
import argparse
import getpass
import os
import re
import sys
import time

from libardurep import datastore, datareporter, serialreader

def interactive_mode(args):
    """
    Helper function to run in interactive mode
    """
    store = datastore.DataStore()
    reporter = datareporter.DataReporter(store, "")

    # hold a dict of serial connections
    threads = {}

    print "Welcome to the interactive mode!"
    print "You have the following options:"
    print "    rounds num                       number of rounds to run threads"
    print "    register [device] [baud]         add a device to observe"
    print "    unregister [device]              remove a device"
    print "    report                           write results to stdout"
    print "    exit                             cleanup and quit"

    # set the default number of rounds to run a thread from the CLI
    rounds = args.rounds

    while True:

        # prompt for user input
        sys.stdout.write(":-> ")
        sys.stdout.flush()

        # get user input
        m = os.read(0,80)[:-1]

        # prepare the modes
        ms = m.split(" ")
        mode = ms[0]

        # standard values from the CLI
        device = args.device
        device_name = re.sub("/dev/", "", args.device)
        baudrate = args.baudrate

        # now do what the user wants - part 1
        if (mode == "rounds" and len(ms) > 1):
            rounds = int(ms[1])
        elif (mode == "exit" or mode == "quit"):
            # clean up
            i = iter(threads)
            for k in i:
                t = threads[k]
                t.halt()
            # and exit
            return
        else:
            # if the device is specified, set it
            if len(ms) > 1:
                if ms[1][0:1] == "/":
                    device = ms[1]
                    device_name = ms[1].sub("/dev/", "", args.device)
                else:
                    device = "/dev/" + ms[1]
                    device_name = ms[1]

            # if device and baudrate are specified, also set the baudrate
            if len(ms) > 2:
                baudrate = ms[2]

            # now do what the user wants
            if (mode == "register"):
                if threads.has_key(device_name):
                    print "This device was already registered"
                else:
                    # create an object that connects to the serial line
                    threads[device_name] = serialreader.SerialReader(device, baudrate, store, rounds)
                    # start recording
                    threads[device_name].start()
            elif (mode == "unregister"):
                if threads.has_key(device_name) and isinstance(threads[device_name], serialreader.SerialReader):
                    # end the recording and remove the device from the list
                    threads[device_name].halt()
                    threads.pop(device_name)
            elif (mode == "report"):
                if reporter.store.last_data_timestamp:
                    reporter.log_stdout()
                else:
                    print "No data has been collected so far, please try again later.."
            else:
                print "This mode is not supported: " + mode
                print "Use one of 'rounds', 'register', 'unregister', "\
                      "'report', or 'exit' ..."

def standard_mode(args):
    """
    Helper function to run the reader for a certain amount of time
    """
    if args.keyword_translation:
        k = decode_keywords(args.keyword_translation)
    else:
        k = None
    store = datastore.DataStore(k)
    reporter = datareporter.DataReporter(store, args.output, None, args.insecure)
    if args.password:
        pw = getpass.getpass()
    else:
        pw = None
    reporter.register_credentials(None, args.user, args.user_file, pw, args.password_file)

    reader = serialreader.SerialReader(args.device, args.baudrate, store, args.rounds)
    reader.start()
    time.sleep(args.seconds)
    reader.halt()
    reporter.log()

def decode_keywords(keywordstring):
    """
    Helper function to read user input
    """
    ks = keywordstring.split(",")
    if len(ks) < 2:
        print "Please provide at least 2 comma separated keywords"
        exit()
    else:
        return ks

if __name__ == '__main__':
    """
    Main function used if started on the command line
    """
    cli_parser = argparse.ArgumentParser(description="Parse data from the arduino and use it for the Flussbad-Demo.")
    cli_parser.add_argument('-b', '--baudrate', default=9600, help='baud rate of the serial line')
    cli_parser.add_argument('-d', '--device', default='/dev/ttyACM0', help='serial device the arduino is connected to')
    cli_parser.add_argument('-i', '--interactive', action="store_true", help='prompt for control and log to stdout')
    cli_parser.add_argument('-I', '--insecure', default=False, action="store_true", help='do not verify certificate on HTTPS POST')
    cli_parser.add_argument('-k', '--keyword_translation', help='list of comma separated keys to expect from the serial input line; mandatory are an ID and a value; default="id,value,unit,threshold"')
    cli_parser.add_argument('-o', '--output', default="", help='output target, where to report the data to. Default is empty for <stdout>, the following URLs are provided yet: "file:///..", "http://..", "https://.."')
    cli_parser.add_argument('-p', '--password', action="store_true", help='prompt for a password')
    cli_parser.add_argument('-P', '--password_file', default='', help='load password from this file, containing the line: \'password: "my secret text"\'')
    cli_parser.add_argument('-r', '--rounds', type=int, default=0, help='how many times to run the serial listener thread (default: 0 / infinite)')
    cli_parser.add_argument('-s', '--seconds', type=int, default=10, help='how long to run if not in interacitve mode')
#    cli_parser.add_argument('-t', '--translation-table-key', help='file containing separate lines with translation pairs for the keywords, e.g. "inkey: outkey"')
#    cli_parser.add_argument('-T', '--translation-table-ids', help='file containing translation pairs for the content of the id-keyword, e.g. "sensor0: box_temp"')
    cli_parser.add_argument('-u', '--user', default='', help='user name')
    cli_parser.add_argument('-U', '--user_file', default='', help='load user name from this file, containing the line: \'user: "my_name"\'')

    args = cli_parser.parse_args()

    if args.interactive:
        interactive_mode(args)
    else:
        standard_mode(args)

