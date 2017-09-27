
import unittest2 as unittest
import json
import serial
import time

from libardurep import datastore, serialreader

class TestSerialReader(unittest.TestCase):
    def setUp(self):
        self.store = datastore.DataStore()
        self.reader = serialreader.SerialReader(None, 9600, self.store, 20)
        self.reader.device_name = "loop://"
        self.reader.device = serial.serial_for_url("loop://", timeout=5)
        self.test_json = ' \n\n[ \n  {"id":"light_value","value":"777"} \n] \n'

    def test_timeout(self):
        # we can not really test the actual timeout of the real serial
        # connection as we have a serial dummy here, but we can test
        # whether readline() timeouts on the dummy and if run() terminats
        # even if no '\n' is received..
        j = 'df'
        self.reader.device.write(j)
        self.reader.run()

    def test_single_run(self):
        self.reader.device.write(self.test_json)
        self.reader.run()
        self.assertEqual("777", self.store.data["light_value"]["value"])

    def test_single_thread(self):
        self.reader = serialreader.SerialReader(None, 9600, self.store, 0)
        self.reader.device = serial.serial_for_url("loop://", timeout=300)
        self.reader.start()
        self.assertTrue(self.reader.is_alive())
        self.reader.halt()
        time.sleep(2)
        self.assertFalse(self.reader.is_alive())

    def test_multi_threads(self):
        first_reader = serialreader.SerialReader(None, 9600, self.store, 0)
        first_reader.device = serial.serial_for_url("loop://", timeout=300)
        second_reader = serialreader.SerialReader(None, 9600, self.store, 0)
        second_reader.device = serial.serial_for_url("loop://", timeout=300)

        first_reader.start()
        self.assertTrue(first_reader.is_alive())
        time.sleep(2)
        self.assertTrue(first_reader.is_alive())
        second_reader.start()
        self.assertTrue(second_reader.is_alive())
        first_reader.halt()
        time.sleep(2)
        self.assertFalse(first_reader.is_alive())
        self.assertTrue(second_reader.is_alive())
        second_reader.halt()
        time.sleep(2)
        self.assertFalse(second_reader.is_alive())

    def test_multi_thread_content(self):
        a = datastore.DataStore()
        b = datastore.DataStore()
        first_reader = serialreader.SerialReader(None, 9600, a, 200)
        first_reader.device = serial.serial_for_url("loop://", timeout=300)
        second_reader = serialreader.SerialReader(None, 9600, b, 200)
        second_reader.device = serial.serial_for_url("loop://", timeout=300)
        third_reader = serialreader.SerialReader(None, 9600, a, 200)
        third_reader.device = serial.serial_for_url("loop://", timeout=300)

        first_reader.device.write(' \n\n[ \n  {"id":"bar","value":"777"} \n] \n')
        second_reader.device.write(' \n\n[ \n  {"id":"foo","value":"666"} \n] \n')
        first_reader.device.write(' \n\n[ \n  {"id":"foo","value":"888"} \n] \n')
        first_reader.start()
        second_reader.start()
        third_reader.start()
        time.sleep(2)
        self.assertEqual("777", a.data["bar"]["value"])
        self.assertEqual("888", a.data["foo"]["value"])
        self.assertEqual("666", b.data["foo"]["value"])
