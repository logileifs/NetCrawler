#File test_code.py
"""docstring"""
#import sys
#import os
import unittest
from classes import netcrawler

"""class CodeTests(unittest.TestCase):"""
class NetCrawlerTests(unittest.TestCase):
	"""docstring"""

	def test_constructor(self):
		arg0 = 'netcrawler'
		arg1 = '192.168.60.254'
		arg2 = 161
		arg3 = 'public'
		arg4 = False
		args = ['', '195.218.195.228', 161, 'public', False]
		arglist = [161, '192.168.60.254/24', 'public', False]
		crawler = netcrawler.Crawler(arg0, arg1, arg2, arg3, arg4)
		assert crawler.address == '195.218.195.228'