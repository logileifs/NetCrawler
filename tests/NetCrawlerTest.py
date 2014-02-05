#File test_code.py
import unittest
import main
from NetCrawler import Crawler

class CodeTests(unittest.TestCase):
	#def test_fn_returns_one(self):
		#assert code.fn() == 1

	#def test_fn2_returns_two(self):
		#assert code.fn2() == 2

	#def test_port(self):
		#assert code.port() == 161

	def test_crawler_port(self):
		crawler = Crawler(161, '195.218.195.228')
		assert crawler.getPort() == 161

	def test_crawler_address(self):
		crawler = Crawler(161, '195.218.195.228')
		assert crawler.getAddress() == '195.218.195.228'