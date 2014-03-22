#File test_code.py
"""Module for testing host.py"""
#import sys
#import os
import unittest
from classes import host
from pyasn1.type import univ

"""class CodeTests(unittest.TestCase):"""
class HostTests(unittest.TestCase):
	"""docstring"""

	def test_hex_to_ip(self):
		test_host = host.Host()
		hex_num = univ.OctetString((192, 168, 60, 254))
		test_ip = test_host.hex_to_ip(hex_num)
		assert test_ip == '192.168.60.254'

	def test_hex_to_mac(self):
		test_host = host.Host()
		hex_num = univ.OctetString((0, 13, 189, 254, 242, 160))
		test_mac = test_host.hex_to_mac(hex_num)
		assert test_mac == '000dbdfef2a0'

