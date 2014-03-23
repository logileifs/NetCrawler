#File test_netcrawler.py
"""Unit testing module for the netcrawler class"""

from classes import netcrawler
import unittest
import ipcalc
#import sys
#import os

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
		arg0 = self.correct_subnet()
		arg1 = self.correct_communitystr()
		arg2 = self.correct_port()
		arg3 = self.correct_debugmode()

		return arg0, arg1, arg2, arg3

	def correct_address_range(self):
		subnet = self.correct_subnet()
		address_range = ipcalc.Network(subnet)

		return address_range


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

	def test_get_address_range(self):
		subnet = self.correct_subnet()
		crawler = netcrawler.Crawler(self.correct_arguments())
		tuple1 = crawler.get_address_range('192.168.60.254/24').to_tuple()
		tuple2 = self.correct_address_range().to_tuple()
		
		assert tuple1 == tuple2
