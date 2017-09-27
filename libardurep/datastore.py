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

    def __init__(self):
        # prepare a dict to store the data
        # this way we can wait for a stable set of values
        self.data = {}
        # remember the time of the last data update
        self.last_data_timestamp = None

    def register_json(self, data):
        """
        Register the contents as JSON
        """
        j = json.loads(data)
        self.last_data_timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat()

        for v in j:
            v["time"] = self.last_data_timestamp
            self.data[v["id"]] = v

    def get_text(self):
        """
        Get the data in text form (i.e. human readable)
        """
        t = "==== " + str(self.last_data_timestamp) + " ====\n"
        for k in self.data:
            if self.data[k].has_key("unit"):
                u = " " + self.data[k]["unit"]
            else:
                u = ""
            t += k + " " + self.data[k]["value"] + u + "\n"
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
        if prettyprint:
            j = j[1:-2] + ",\n"
        else:
            j = j[1:-1] + ","
        return j

