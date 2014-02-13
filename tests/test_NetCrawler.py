#File test_code.py
import sys
import os
import unittest
from classes import Crawler

class CodeTests(unittest.TestCase):

	def test_crawler_port(self):
		crawler = Crawler(161, '195.218.195.228')
		assert crawler.getPort() == 161

	def test_crawler_address(self):
		crawler = Crawler(161, '195.218.195.228')
		assert crawler.getAddress() == '195.218.195.228'

	def test_crawler_hello(self):
		crawler = Crawler(161, '195.218.195.228')
		assert crawler.getHello() == 'hello'

	def test_crawler_helloworld(self):
		crawler = Crawler(161, '195.218.195.228')
		assert crawler.getHelloWorld() == 'hello world'