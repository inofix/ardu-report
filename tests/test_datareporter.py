
from base64 import b64encode
import unittest2 as unittest
import datetime
import json
import re
import tempfile

from libardurep import datastore, datareporter

class TestDataReport(unittest.TestCase):
    def setUp(self):
        self.store = datastore.DataStore()
        self.reporter = datareporter.DataReporter(self.store)

    def test_log(self):
        # this is tested in the actual log_*() respectively
        pass

    def test_log_stdout(self):
        # this is tested anyway in self.store.get_text()
        pass

    def test_log_file(self):
        self.store.register_json('[{"id":"foo"}]')

        tf = tempfile.NamedTemporaryFile()

        self.reporter.log_file("file:///" + tf.name)
        with open(tf.name, "r") as fh:
            fc = fh.read()
        sc = self.store.get_json_tuples(True)

        self.assertEqual(sc, fc)

        self.reporter.log_file("file:///" + tf.name)
        with open(tf.name, "r") as fh:
            fc = fh.read()

        self.assertEqual(sc + sc, fc)

    def test_log_post(self):
        # Create a local http server? ...
        pass

    def test_log_ssh(self):
        # not implemented yet
        pass

    def test_register_credentials(self):
        tf = tempfile.NamedTemporaryFile()

        u = "me"
        p = "secret"

        self.reporter.register_credentials({"user":u,"password":p})
        self.assertEqual(self.reporter.credentials["user"], u)
        self.assertEqual(self.reporter.credentials["password"], p)
        self.reporter.credentials = {}

        self.reporter.register_credentials(None, u, None, p, None)
        self.assertEqual(self.reporter.credentials["user"], u)
        self.assertEqual(self.reporter.credentials["password"], p)
        self.reporter.credentials = {}

        with open(tf.name, "w") as fh:
            fh.write("user: " + u + "\npassword: " + p + "\n")

        self.reporter.register_credentials(None, None, tf.name, None, tf.name)
        self.assertEqual(self.reporter.credentials["user"], u)
        self.assertEqual(self.reporter.credentials["password"], p)

        b = b64encode(u + ":" + p).decode("ascii")
        self.assertEqual(self.reporter.credentials["base64"], b)

