
import unittest2 as unittest
import datetime
import json
import re

from libardurep import datastore

class TestDataStore(unittest.TestCase):
    def setUp(self):
        self.store = datastore.DataStore()

    def test_parse_schema(self):
        with open("./schemas/meta-schema.json", "r") as fh:
            m = fh.read()
        with open("./schemas/default-schema.json", "r") as fh:
            s = fh.read()
        with self.assertRaises(TypeError):
            self.store.parse_schemas(s, None, None, None)
        self.store.parse_schemas(s, m, None, None)
        with open("./schemas/meta-schema.json", "r") as fh:
            m = fh.read()
        with open("./schemas/default-schema.json", "r") as fh:
            s = fh.read()
        with self.assertRaises(TypeError):
            self.store.parse_schemas(None, None, s, None)
        self.store.parse_schemas(None, None, s, m)
        self.store.parse_schemas(s, m, s, m)
        with open("./schemas/meta-schema.json", "r") as fh:
            ma = fh.read()
        with open("./examples/extended-input-schema.json", "r") as fh:
            sa = fh.read()
        self.store.parse_schemas(sa, ma, None, None)
        with open("./examples/custom-output-meta-schema.json", "r") as fh:
            mb = fh.read()
        with open("./examples/custom-output-schema.json", "r") as fh:
            sb = fh.read()
        self.store.parse_schemas(None, None, sb, mb)
        self.store.parse_schemas(sa, ma, sb, mb)

    def test_register_json(self):
        j = '[ {"id":"light_value","value":"777"} ]'
        j_son = json.loads(j)

        self.store.register_json(j)

        self.assertEqual("777", self.store.data["light_value"]["value"])
        self.assertEqual(j_son[0]["value"], self.store.data["light_value"]["value"])

    def test_datetime(self):
        self.assertIs(self.store.last_data_timestamp, None)

        j = '[ {"id":"light_value","value":"777"} ]'
        j_son = json.loads(j)

        self.store.register_json(j)
        self.assertIsNot(self.store.last_data_timestamp, None)

    def test_get_text(self):
        j = '[ {"id":"a","value":"8","unit":"m"}, {"id":"b","value":"9"} ]'
        d = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
        d = re.sub(":..$", ":XX", d)
        self.store.register_json(j)

        t0 = "==== " + d + " ===="
        t1 = "a 8m"
        t2 = "b 9"

        result = self.store.get_text()
        rs = result.split("\n")
        r0 = re.sub(":.. ====", ":XX ====", rs[0].encode("ascii"))
        r1 = rs[1]
        r2 = rs[2]

        self.assertEqual(t0, r0)
        self.assertEqual(t1, r1)
        self.assertEqual(t2, r2)

    def test_get_tranlated_data(self):
        with open("./schemas/meta-schema.json", "r") as fh:
            ma = fh.read()
        with open("./schemas/default-schema.json", "r") as fh:
            sa = fh.read()
        with open("./examples/custom-output-meta-schema.json", "r") as fh:
            mb = fh.read()
        with open("./examples/custom-output-schema.json", "r") as fh:
            sb = fh.read()
        self.store.parse_schemas(sa, ma, sb, mb)
        j = '[ {"id":"a","value":"8","unit":"m"}, {"id":"b","value":"9"} ]'
        self.store.register_json(j)
        d = self.store.get_translated_data()
        self.assertTrue(d.has_key('a'))
        self.assertTrue(d.has_key('b'))
        self.assertTrue(d['a'].has_key('ourVeryCustomSensorName'))
        self.assertTrue(d['a']['ourVeryCustomSensorName'] == 'a')
        self.assertTrue(d['b'].has_key('sensorValue'))

    def test_get_json(self):
        j = '[{"id":"foo","value":"777"}]'
        self.store.register_json(j)

        j_son = json.loads(self.store.get_json())
        self.assertEqual(j_son[0]["value"], "777")

        j_son = json.loads(self.store.get_json(True))
        self.assertEqual(j_son[0]["value"], "777")

        j0 = self.store.get_json()
        j1 = self.store.get_json(True)
        self.assertTrue(len(j0) < len(j1))

    def test_get_json_tuples(self):
        j = '[ {"id":"foo","value":"777"} ]'
        self.store.register_json(j)

        j0 = self.store.get_json()
        jt0 = self.store.get_json_tuples()
        j1 = self.store.get_json(True)
        jt1 = self.store.get_json_tuples(True)

        self.assertEqual(j0[1:-1] + ",", jt0)
        self.assertEqual(len(j1), len(jt1) + 1)

