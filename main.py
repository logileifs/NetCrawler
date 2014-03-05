#! /usr/bin/env python
#File main.py

import os
import sys
from classes import netcrawler
from classes import drawnetwork

def main():
	"""
	This is a test for the CI server
	Another test for the CI server
	"""

	print 'Number of arguments:', len(sys.argv), 'arguments'
	
	address, port, community, debugMode = parseInput(sys.argv)
	crawler = netcrawler.Crawler(port, address, community, debugMode)

	print('Address is ' + str(crawler.address) + ' Port is ' + str(crawler.port))


	crawler.printHosts()

	for host in crawler.hostList:
		if not host.visited:
			crawler.getInfo(host)

	crawler.printHosts()

	crawler.generateXML()

	drawNet = drawnetwork.DrawNetwork()
	drawNet.draw(crawler.network)



def parseInput(args):
	foundPort = False
	foundAddress = False
	foundCommunity = False
	debugMode = False

	for arg in args:
		if(arg == args[0]):
			continue
		if(arg[0:2] == 'p='):
			foundPort = True
			port = int(arg[2:])
		if(arg[0:2] == 'a='):
			foundAddress = True
			address = str(arg[2:])
		if(arg[0:2] == 'c='):
			foundCommunity = True
			community = str(arg[2:])
		if(arg[0:1] == 'd'):
			debugMode = True

	if(not foundAddress):
		exit('Must provide an address')
	if(not foundPort):
		port = 161
		print('No port argument found, using default port 161')
	if(not foundCommunity):
		community = 'public'
		print('Default community set to public')

	return address, port, community, debugMode


def exit(why):
	print(why)
	sys.exit(1)


if __name__ == "__main__":
	main()