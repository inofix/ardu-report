"""
MODULE:       serialreader
PURPOSE:      get the data from the serial console and store it in the
              data store.
AUTHOR(S):    michael lustenberger inofix.ch
COPYRIGHT:    (C) 2017 by Michael Lustenberger and INOFIX GmbH

              This program is free software under the GNU General Public
              License (v3).
"""

import json
import serial
import threading

class SerialReader(threading.Thread):
    """
    Reader class for connecting to an end device and reading its output
    """

    def __init__(self, device, baudrate, store, rounds):
        """
        Initialize the serial reader class
            device        device name to connect to
            baudrate      the baud rate for the serial line
            store        the data store object to send the data to
            rounds        number of rounds to run / listen for input
        """
        threading.Thread.__init__(self)
        self.device = device
        self.baudrate = baudrate
        self.store = store
        self.rounds = rounds
        self.do_run = True

    def run(self):
        """
        Open a connection over the serial line and receive data lines
        """
        try:
            arduino_serial = serial.Serial(self.device, self.baudrate);

            data = ""

            while (self.do_run):
                if (arduino_serial.inWaiting() > 1):
                    l = arduino_serial.readline()[:-2]

                    if (l == "["):
                        # start recording
                        data = "["
                    elif (l == "]") and (len(data) > 4) and (data[0] == "["):
                        # now parse the input
                        data = data + "]"
                        self.store.register_json(data)
                        if self.rounds == 1:
                            self.do_run = False
                        elif self.rounds > 1:
                            self.rounds -= 1
                    elif (l[0:3] == "  {"):
                        # this is a data line
                        data = data + " " + l

        except serial.serialutil.SerialException:
            print "Could not connect to the serial line at " + self.device

    def halt(self):
        """
        Tell the this object to stop working after the next round
        """
        self.do_run = False

