
import unittest2 as unittest
import datetime
import json
import re

from libardurep import datastore

class TestDataStore(unittest.TestCase):
    def setUp(self):
        self.store = datastore.DataStore()

    def test_register_json(self):
        j = '[ {"name":"light_value","value":"777"} ]'
        j_son = json.loads(j)

        self.store.register_json(j)

        self.assertEqual("777", self.store.data["light_value"]["value"])
        self.assertEqual(j_son[0]["value"], self.store.data["light_value"]["value"])

    def test_datetime(self):
        self.assertIs(self.store.last_data_timestamp, None)

        j = '[ {"name":"light_value","value":"777"} ]'
        j_son = json.loads(j)

        self.store.register_json(j)
        self.assertIsNot(self.store.last_data_timestamp, None)

    def test_get_text(self):
        j = '[ {"name":"a","value":"8","unit":"m"}, {"name":"b","value":"9"} ]'
        d = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
        d = re.sub(":..$", ":XX", d)
        self.store.register_json(j)

        t0 = "==== " + d + " ===="
        t1 = "a 8 m"
        t2 = "b 9"

        result = self.store.get_text()
        rs = result.split("\n")
        r0 = re.sub(":.. ====", ":XX ====", rs[0].encode("ascii"))
        r1 = rs[1]
        r2 = rs[2]

        self.assertEqual(t0, r0)
        self.assertEqual(t1, r1)
        self.assertEqual(t2, r2)

    def test_get_json(self):
        j = '[{"name":"foo","value":"777"}]'

        self.store.register_json(j)
        j_son = json.loads(self.store.get_json())

        self.assertEqual(j_son[0]["value"], "777")

    def test_get_json_tuples(self):
        j = '[ {"name":"foo","value":"777"} ]'
        self.store.register_json(j)

        self.assertEqual(self.store.get_json()[1:-1], self.store.get_json_tuples())

