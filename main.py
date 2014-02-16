#! /usr/bin/env python
#File main.py

import os
import sys
from classes import netcrawler

def main():
	"""
	This is a test for the CI server
	Another test for the CI server
	"""

	print 'Number of arguments:', len(sys.argv), 'arguments'
	
	address, port = parseInput(sys.argv)
	crawler = netcrawler.Crawler(port, address)

	print('Address is ' + str(crawler.address) + ' Port is ' + str(crawler.port))

	if crawler.checkEntryPoint(crawler.address):
		print('entry point answers snmp CDP requests')
	numberOfNeighbors = crawler.getNeighbors(crawler.hosts[0])	# get numbers of first host
	numberOfNeighbors = crawler.getNeighbors(crawler.hosts[1])
	numberOfNeighbors = crawler.getNeighbors(crawler.hosts[2])
	"""if numberOfNeighbors > 0:
		print('found ' + str(numberOfNeighbors) + ' neighbors')

	for host in crawler.hosts:
		if not host.visited:
			numberOfNeighbors = crawler.getNeighbors(host.ip)
			host.visited = True"""


def parseInput(args):
	foundPort = False
	foundAddress = False

	for arg in args:
		if(arg == args[0]):
			continue
		if(arg[0:5] == 'port='):
			foundPort = True
			port = int(arg[5:])
		if(arg[0:8] == 'address='):
			foundAddress = True
			address = str(arg[8:])

	if(not foundAddress):
		exit('Must provide an address')
	if(not foundPort):
		port = 161
		print('No port argument found, using default port 161')

	return address, port


def exit(why):
	print(why)
	sys.exit(1)


if __name__ == "__main__":
	main()