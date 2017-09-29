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
from jsonschema import Draft4Validator as Validator

class DataStore(object):
    """
    This store is used to collect sensor data as separate tuples
    per sensor. Newer data overwrites older data and incomplete
    runs will eventually accumulate to full sets over time.
    """

    def __init__(self, in_schema=None, in_meta_schema=None, \
                        out_schema=None, out_meta_schema=None):
        # prepare a timestamp to remember the last data update
        self.last_data_timestamp = None
        # prepare a dict to store the data
        # this way we can wait for a stable set of values
        self.data = {}
        # define the default keywords
        ## mandatory
        self.id_key = "id"
        self.value_key = "value"
        ## optional but well known
        self.unit_key = "unit"
        self.threshold_key = "threshold"
        ## special time keys
        ### report time
        self.time_key = "time"
        ### if sensor transmits a timestamp
        self.sensor_time_key = "sensor_timestamp"
        self.fallback_time_key = "report_timestamp"
        ## the whole well known as an "input: output" map...
        self.well_now_keys = {
            self.id_key: self.id_key,
            self.value_key: self.value_key,
            self.unit_key: self.unit_key,
            self.threshold_key: self.threshold_key,
            self.time_key: self.sensor_time_key
        }
        ## the rest to be set based on the schema files
        self.other_keys = {}

    def parse_schema(data, schema, meta_schema):
        # load the two JSON schema objects
        m = json.load(meta_schema)
        s = json.load(schema)
        # add some sanity argument before changing the config
        Validator(m).validate(s)
        # search for the keys
        for k in s["items"]["properties"]:
            v = s["items"]["properties"][k]
            if v.has_key["use"]:
                if v["use"] == "identifier":
                    self.id_key = k
                elif v["use"] == "value":
                    self.value_key = k
                elif v["use"] == "unit":
                    self.unit_key = k
                elif v["use"] == "threshold":
                    self.threshold_key = k
                elif v["use"] == "timestamp":
                    if k == self.time_key:
                        self.time_key = self.fallback_time_key
                    self.sensor_time_key = k
                elif v["use"] == "other":
                    self.other_keys.append(k, "")

    def register_json(self, data):
        """
        Register the contents as JSON
        """
        j = json.loads(data)
        self.last_data_timestamp = \
                datetime.datetime.utcnow().replace(microsecond=0).isoformat()

        try:
            for v in j:
                # prepare the sensor entry container
                self.data[v[self.id_key]] = {}
                # add the mandatory entries
                self.data[v[self.id_key]][self.id_key] = \
                                            v[self.id_key]
                self.data[v[self.id_key]][self.value_key] = \
                                            v[self.value_key]
                # add the optional well known entries if provided
                if v.has_key(self.unit_key):
                    self.data[v[self.id_key]][self.unit_key] = \
                                            v[self.unit_key]
                if v.has_key(self.threshold_key):
                    self.data[v[self.id_key]][self.threshold_key] = \
                                            v[self.threshold_key]
                # add any further entries found
                for k in self.other_keys:
                    if v.has_key(k):
                        self.data[v[self.id_key]][k] = v[k]
                # add the custom sensor time
                if v.has_key(self.sensor_time_key):
                    self.data[v[self.sensor_time_key]][self.sensor_time_key] = \
                                            v[self.sensor_time_key]
                # last: add the time the data was received (overwriting any
                # not properly defined timestamp that was already there)
                self.data[v[self.id_key]][self.time_key] = \
                                            self.last_data_timestamp
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
            t += k + " " + str(self.data[k][self.value_key])
            u = ""
            if self.data[k].has_key(self.unit_key):
                u = self.data[k][self.unit_key]
                t += u
            if self.data[k].has_key(self.threshold_key):
                if (self.data[k][self.threshold_key] < \
                                    self.data[k][self.value_key]):
                    t += " !Warning: Value is over threshold: " + \
                                str(self.data[k][self.threshold_key]) + "!"
                else:
                    t += " (" + str(self.data[k][self.threshold_key]) + u + ")"
            for l in self.other_keys:
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

