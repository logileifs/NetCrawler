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
		arglist = [161, '192.168.60.254/24', 'public', False]
		print(arglist[0])
		print(arglist[1])
		print(arglist[2])
		crawler = netcrawler.Crawler(arglist)
		assert crawler.address == '195.218.195.228'