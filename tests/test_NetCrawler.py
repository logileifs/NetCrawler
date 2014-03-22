#File test_netcrawler.py
"""Unit testing module for the netcrawler class"""
#import sys
#import os
import unittest
from classes import netcrawler

class NetCrawlerTests(unittest.TestCase):
	"""docstring"""

	def correct_scriptname(self):
		return './classes/netcrawler.py'

	def wrong_scriptname(self):
		return './wrong/wrong.py'

	def correct_subnet(self):
		return '192.168.60.254/24'

	def wrong_subnet(self):
		return '127.0.0.1/32'

	def correct_port(self):
		return 161

	def wrong_port(self):
		return 8080

	def correct_communitystr(self):
		return 'menandmice'

	def wrong_communitystr(self):
		return 'public'

	def correct_debugmode(self):
		return False

	def wrong_debugmode(self):
		return True

	def correct_arguments(self):
		#arg0 = self.correct_scriptname()
		arg0 = self.correct_subnet()
		arg1 = self.correct_communitystr()
		arg2 = self.correct_port()
		arg3 = self.correct_debugmode()

		return arg0, arg1, arg2, arg3

	def test_constructor_subnet_argument(self):
		crawler = netcrawler.Crawler(self.correct_arguments())
		assert crawler.subnet == self.correct_subnet()

	def test_constructor_communitystr_argument(self):
		crawler = netcrawler.Crawler(self.correct_arguments())
		assert crawler.community_str == self.correct_communitystr()

	def test_constructor_port_argument(self):
		crawler = netcrawler.Crawler(self.correct_arguments())
		assert crawler.port == self.correct_port()

	def test_constructor_debugmode_argument(self):
		crawler = netcrawler.Crawler(self.correct_arguments())
		assert crawler.debug_mode == self.correct_debugmode()
