
import unittest2 as unittest
import json
from jsonschema import Draft4Validator as Validator
import os

class TestJSON(unittest.TestCase):
    def setUp(self):
        with open("./schemas/meta-schema.json", "r") as fh:
            self.meta_schema = json.loads(fh.read())
        with open("./schemas/default-schema.json", "r") as fh:
            self.schema = json.loads(fh.read())
        with open("./examples/input.json") as fh:
            self.example = json.loads(fh.read())

    def test_schema(self):
        Validator(self.meta_schema).validate(self.schema)

    def test_example(self):
        Validator(self.schema).validate(self.example)

