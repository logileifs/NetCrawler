#File test_code.py
"""Module for testing main.py"""

import sys
import os
import unittest
import main

class MainTests(unittest.TestCase):
	"""docstring"""
	
	"""def test_parse_input_address(self):
		args = ['', 'a=195.218.195.228', 'p=161', 'c=public', 'd']
		address, port, community, debugMode = main.parse_input(args)
		assert address == '195.218.195.228'
	
	def test_parse_input_port(self):
		args = ['', 'a=195.218.195.228', 'p=1337', 'c=public', 'd']
		address, port, community, debugMode = main.parse_input(args)
		assert port == 1337

	def test_parse_input_default_port(self):
		args = ['', 'a=195.218.195.228', 'c=public', 'd']
		address, port, community, debugMode = main.parse_input(args)
		assert port == 161

	def test_parse_input_default_community(self):
		args = ['', 'a=195.218.195.228', 'p=1337', 'c=public', 'd']
		address, port, community, debugMode = main.parse_input(args)
		assert community == 'public'
	 
	def test_parse_input_no_arguments(self):
		args = []
		with self.assertRaises(SystemExit) as cm:
			address, port = main.parse_input(args)
		self.assertEqual(cm.exception.code, 1)"""