#! /usr/bin/env python
#File code.py

import os
import sys
from pysnmp.entity.rfc3413.oneliner import cmdgen

from classes import NetCrawler

def main():
	"""
	This is a test for the CI server
	Another test for the CI server
	"""

	cmdGen = cmdgen.CommandGenerator()

	print 'Number of arguments:', len(sys.argv), 'arguments'
	print 'Argument List:', str(sys.argv)
	
	address, port = parseInput(sys.argv)
	crawler = NetCrawler.Crawler(port, address)

	print('Address is ' + str(crawler.address) + ' Port is ' + str(crawler.port))

	errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
		cmdgen.CommunityData('public'),
		#cmdgen.UdpTransportTarget(('195.218.195.228', 161)),
		#cmdgen.UdpTransportTarget(('192.168.1.92', 161)),
	    cmdgen.UdpTransportTarget((crawler.address, crawler.port)),
		cmdgen.MibVariable('SNMPv2-MIB', 'sysDescr', 0),
		lookupNames=True, lookupValues=True)

	# Check for errors and print out results
	if errorIndication:
		print(errorIndication)
	elif errorStatus:
		print(errorStatus)
	else:
		print('port number: ' + str(port))
		for name, val in varBinds:
			print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))


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