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

        for v in j:
            self.data[v["name"]] = v

        self.last_data_timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat()

