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
	print 'Argument List:', str(sys.argv)
	
	address, port = parseInput(sys.argv)
	crawler = netcrawler.Crawler(port, address)

	print('Address is ' + str(crawler.address) + ' Port is ' + str(crawler.port))

#	crawler.getPorts()
#	crawler.getMacs()
#	crawler.getMacTable()
#	crawler.getIPs()
#	crawler.getMacOnPort()
#	crawler.getMacForIP()
	crawler.getVLANs()

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