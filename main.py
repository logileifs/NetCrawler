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

	print 'Number of arguments:', len(sys.argv), 'arguments.'
	print 'Argument List:', str(sys.argv)
	if len(sys.argv) > 1:
		print('argv1: ' + str(sys.argv[1]))
		print('argv2: ' + str(sys.argv[2]))
		address = sys.argv[1]
		port = sys.argv[2]
		crawler = NetCrawler(address, port)
	else:
		address = 'demo.snmplabs.com'
		port = 161
		crawler = NetCrawler(address, port)

	errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
		cmdgen.CommunityData('public'),
		#cmdgen.UdpTransportTarget(('195.218.195.228', 161)),
		cmdgen.UdpTransportTarget(('192.168.1.92', 161)),
		cmdgen.MibVariable('SNMPv2-MIB', 'sysDescr', 0),
		lookupNames=True, lookupValues=True
	)

	# Check for errors and print out results
	if errorIndication:
		print(errorIndication)
	elif errorStatus:
		print(errorStatus)
	else:
		print('port number: ' + port())
		for name, val in varBinds:
			print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))

def port():
	return crawler.port

if __name__ == "__main__":
	main()