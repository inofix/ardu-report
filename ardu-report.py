#!/usr/bin/env python

"""
PURPOSE:      read the serial output of one or more arduino boards
              and store the sensor values..
DEPENDENCY:   python >2.7, see requirements.txt
PLATTFORM:    currently only unix/linux is supported
AUTHOR(S):    michael lustenberger inofix.ch
COPYRIGHT:    (C) 2017 by Michael Lustenberger and INOFIX GmbH

              This program is free software under the GNU General Public
              License (>=v2).
"""

import configargparse
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
    # URL is always stdout as we are in interactive mode..
    store = datastore.DataStore()
    reporter = datareporter.DataReporter(store, "")

    # hold a dict of serial connections
    threads = {}

    # user feedback
    print("Welcome to the interactive mode!")
    print("You have the following options:")
    print("    rounds num                       number of rounds to run threads")
    print("    register [device] [baud]         add a device to observe")
    print("    unregister [device]              remove a device")
    print("    report                           write results to stdout")
    print("    exit                             cleanup and quit")

    # set the default number of rounds to run a thread from the CLI
    rounds = args.rounds

    # standard device values from the CLI
    device_name = args.device
    path_pattern = re.compile("/+dev/+")
    device_short_name = path_pattern.sub("", args.device)
    baudrate = int(args.baudrate)

    while True:

        try:
            # prompt for user input
            sys.stdout.write(":-> ")
            sys.stdout.flush()

            # get user input
            m = os.read(0,80)[:-1].decode("UTF-8")

            # prepare the modes
            ms = m.split(" ")
            mode = ms[0]

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
            else: # everything else may accept arguments
                # if the device is specified, set it
                if len(ms) > 1:
                    if ms[1][0:1] == "/":
                        device_name = ms[1]
                        device_short_name = path_pattern.sub("", ms[1])
                    else:
                        device_name = "/dev/" + ms[1]
                        device_short_name = ms[1]

                # if device and baudrate are specified, also set the baudrate
                if len(ms) > 2:
                    baudrate = int(ms[2])

                # now do what the user wants - part 2
                if (mode == "register"):
                    if device_short_name in threads:
                        print("This device (" + device_name + \
                                            ") was already registered")
                    else:
                        # create an object that connects to the serial line
                        threads[device_short_name] = serialreader.SerialReader(\
                                        device_name, baudrate, store, rounds)
                        # start recording
                        threads[device_short_name].start()
                elif (mode == "unregister"):
                    if device_short_name in threads and isinstance(threads[\
                            device_short_name], serialreader.SerialReader):
                        # end the recording and remove the device from the list
                        threads[device_short_name].halt()
                        threads.pop(device_short_name)
                elif (mode == "report"):
                    if reporter.store.last_data_timestamp:
                        reporter.log_stdout()
                    else:
                        print("No data has been collected so far, please"\
                                "try again later..")
                else:
                    print("This mode is not supported: " + mode)
                    print("Use one of 'rounds', 'register', 'unregister', "\
                          "'report', or 'exit' ...")
        except Exception as e:
            print("The following Error has occured: " + str(e))
            print("Please try again, or start over by typing 'exit'")

def create_store(args):
    if args.json_input_schema and args.meta_input_schema:
        with open(args.json_input_schema, "r") as fh:
            s_in = fh.read()
        with open(args.meta_input_schema, "r") as fh:
            m_in = fh.read()
    else:
        s_in = None
        m_in = None
    if args.json_output_schema and args.meta_output_schema:
        with open(args.json_output_schema, "r") as fh:
            s_out = fh.read()
        with open(args.meta_output_schema, "r") as fh:
            m_out = fh.read()
    else:
        s_out = None
        m_out = None
    return datastore.DataStore(s_in, m_in, s_out, m_out)

def standard_mode(args):
    """
    Helper function to run the reader for a certain amount of time
    """
    store = create_store(args)
    reporter = datareporter.DataReporter(store, args.output, None, not args.insecure)
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

if __name__ == '__main__':
    """
    Main function used if started on the command line
    """
    p = configargparse.ArgumentParser(default_config_files=['/etc/ardu_report/config', '~/.ardu_report/config', './.ardu_report.conf'], description="Parse data from the arduino and report it anywhere.\n\n")
    p.add_argument('-b', '--baudrate', default=9600, help='baud rate of the serial line')
    p.add('-c', '--config', required=False, is_config_file=True, help='config file path')
    p.add_argument('-d', '--device', default='/dev/ttyACM0', help='serial device the arduino is connected to')
    p.add_argument('-i', '--interactive', action="store_true", help='prompt for control and log to stdout. Useful for testing connected controller boards.')
    p.add_argument('-I', '--insecure', default=False, action="store_true", help='do not verify certificate on HTTPS POST')
    p.add_argument('-j', '--json_input_schema', help='file path to the JSON schema for the data coming from the sensor device.')
    p.add_argument('-J', '--json_output_schema', help='file path to the JSON schema for the data to be reported.')
    p.add_argument('-m', '--meta_input_schema', help='file path to the JSON meta schema for the data coming from the sensor device. This will validate the "--json_input_schema."')
    p.add_argument('-M', '--meta_output_schema', help='file path to the JSON meta schema for the data to be reported. This will validate the "--json_output_schema.')
    p.add_argument('-o', '--output', default="", help='output target, where to report the data to. Default is empty for <stdout>, the following URLs are provided yet: "file:///..", "http://..", "https://.."')
    p.add_argument('-p', '--password', action="store_true", help='prompt for a password')
    p.add_argument('-P', '--password_file', default='', help='load password from this file, containing the line: \'password: "my secret text"\'')
    p.add_argument('-r', '--rounds', type=int, default=10, help='how many times to run the serial listener thread (default: 100; use 0 for infinite)')
    p.add_argument('-s', '--seconds', type=int, default=10, help='how long to run if not in interacitve mode')
    p.add_argument('-u', '--user', default='', help='user name')
    p.add_argument('-U', '--user_file', default='', help='load user name from this file, containing the line: \'user: "my_name"\'')

    args = p.parse_args()

    if args.json_input_schema and not args.meta_input_schema:
        print("If a 'json_input_schema' is provided, the 'meta_input_schema' is required.")
        exit()
    if args.json_output_schema and not args.meta_output_schema:
        print("If a 'json_output_schema' is provided, the 'meta_output_schema' is required.")
        exit()

    if args.interactive:
        interactive_mode(args)
    else:
        standard_mode(args)

