"""
MODULE:       datastore
PURPOSE:      store sensor data sets
AUTHOR(S):    michael lustenberger inofix.ch
COPYRIGHT:    (C) 2017 by Michael Lustenberger and the INOFIX GmbH

              This program is free software under the GNU General Public
              License (v3).
"""

import datetime
import json

class DataStore(object):
    """
    This store is used to collect sensor data as separate tuples
    per sensor. Newer data overwrites older data and incomplete
    runs will eventually accumulate to full sets over time.
    """

    def __init__(self, input_keys=None, time_key=None):
        # prepare a dict to store the data
        # this way we can wait for a stable set of values
        self.data = {}
        # remember the time of the last data update
        self.last_data_timestamp = None
        # keywords to use
        if time_key:
            self.time_key = time_key
        else:
            self.time_key = "time"
        if input_keys:
            self.id_key = input_keys[0]
            self.value_key = input_keys[1]
            self.opt_keys = input_keys[2:]
        else:
            self.id_key = "id"
            self.value_key = "value"
            self.opt_keys = [ "unit", "threshold" ]

    def register_json(self, data):
        """
        Register the contents as JSON
        """
        j = json.loads(data)
        self.last_data_timestamp = \
                datetime.datetime.utcnow().replace(microsecond=0).isoformat()

        try:
            for v in j:
                self.data[v[self.id_key]] = {}
                self.data[v[self.id_key]][self.id_key] = \
                                            v[self.id_key]
                self.data[v[self.id_key]][self.value_key] = \
                                            v[self.value_key]
                self.data[v[self.id_key]][self.time_key] = \
                                            self.last_data_timestamp
                for w in self.opt_keys:
                    if v.has_key(w):
                        self.data[v[self.id_key]][w] = v[w]
        except KeyError as e:
            print "The main key was not found on the serial input line: " + \
                    str(e)
        except ValueError as e:
            print "No valid JSON string received. Waiting for the next turn."
            print "The error was: " + str(e)

    def get_text(self):
        """
        Get the data in text form (i.e. human readable)
        """
        t = "==== " + str(self.last_data_timestamp) + " ====\n"
        for k in self.data:
            t += k + " " + self.data[k][self.value_key]
            for l in self.opt_keys:
                if self.data[k].has_key(l):
                    t += " " + self.data[k][l]
            t += "\n"
        return t

    def get_json(self, prettyprint=False):
        """
        Get the data in JSON form
        """
        j = []
        for k in self.data:
            j.append(self.data[k])
        if prettyprint:
            j = json.dumps(j, indent=2, separators=(',',': '))
        else:
            j = json.dumps(j)
        return j

    def get_json_tuples(self, prettyprint=False):
        """
        Get the data as JSON tuples
        """
        j = self.get_json(prettyprint)
        if len(j) > 2:
            if prettyprint:
                j = j[1:-2] + ",\n"
            else:
                j = j[1:-1] + ","
        else:
            j = ""
        return j

