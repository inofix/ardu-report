
import unittest2 as unittest
import json
from jsonschema import Draft4Validator as Validator
import os

class TestJSON(unittest.TestCase):
    def test_json_schema(self):
        with open("./schemas/meta-schema.json", "r") as fh:
            meta_schema = json.loads(fh.read())
        with open("./schemas/default-schema.json", "r") as fh:
            schema = json.loads(fh.read())
        Validator(meta_schema).validate(schema)

    def test_json_example(self):
        with open("./schemas/default-schema.json", "r") as fh:
            schema = json.loads(fh.read())
        with open("./examples/input.json") as fh:
            example = json.loads(fh.read())
        Validator(schema).validate(example)

    def test_json_extended_schema(self):
        with open("./schemas/meta-schema.json", "r") as fh:
            meta_schema = json.loads(fh.read())
        with open("./examples/extended-input-schema.json", "r") as fh:
            schema = json.loads(fh.read())
        Validator(meta_schema).validate(schema)

    def test_json_extended_example(self):
        with open("./examples/extended-input-schema.json", "r") as fh:
            schema = json.loads(fh.read())
        with open("./examples/extended-input.json") as fh:
            example = json.loads(fh.read())
        Validator(schema).validate(example)


