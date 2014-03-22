#File test_code.py
"""docstring"""
#import sys
#import os
import unittest
from classes import netcrawler

class NetCrawlerTests(unittest.TestCase):
	"""docstring"""

	def correct_port(self):
		return 161

	def correct_arguments(self):
		arg0 = 'netcrawler'
		arg1 = '192.168.60.254/24'
		arg2 = 161
		arg3 = 'menandmice'
		arg4 = False

		return arg0, arg1, arg2, arg3, arg4

	"""arg0 = 'netcrawler'
	arg1 = '192.168.60.254/24'
	arg2 = 161
	arg3 = 'public'
	arg4 = False"""

	def test_constructor_subnet_argument(self):
		arg0 = 'netcrawler'
		arg1 = '192.168.60.254/24'
		arg2 = 161
		arg3 = 'public'
		arg4 = False
		crawler = netcrawler.Crawler(arg0, arg1, arg2, arg3, arg4)
		assert crawler.subnet == '192.168.60.254/24'

	#def test_constructor_port_argument(self):
		#pass