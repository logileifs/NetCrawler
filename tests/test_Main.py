#File test_code.py
import sys
import os
import unittest
import main

class MainTests(unittest.TestCase):
	
	def test_parseInput_address(self):
		args = ['', 'a=195.218.195.228', 'p=161', 'c=public', 'd']
		address, port, community, debugMode = main.parseInput(args)
		assert address == '195.218.195.228'
	
	def test_parseInput_port(self):
		args = ['', 'a=195.218.195.228', 'p=1337', 'c=public', 'd']
		address, port, community, debugMode = main.parseInput(args)
		assert port == 1337

	def test_parseInput_defaultPort(self):
		args = ['', 'a=195.218.195.228', 'c=public', 'd']
		address, port, community, debugMode = main.parseInput(args)
		assert port == 161

	def test_parseInput_defaultCommunity(self):
		args = ['', 'a=195.218.195.228', 'p=1337', 'c=public', 'd']
		address, port, community, debugMode = main.parseInput(args)
		assert community == 'public'
	 
	def test_parseInput_noArguments(self):
		args = []
		with self.assertRaises(SystemExit) as cm:
			address, port = main.parseInput(args)
		self.assertEqual(cm.exception.code, 1)	