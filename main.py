#! /usr/bin/env python
#File main.py
"""docstring"""

#import os
import sys
from classes import netcrawler
from classes import drawnetwork

def main():
	"""Main function to invoke the NetCrawler"""

	print 'Number of arguments:', len(sys.argv), 'arguments'
	
	address, port, community, debug_mode = parse_input(sys.argv)
	crawler = netcrawler.Crawler(port, address, community, debug_mode)

	#print('Address is ' + str(crawler.address) + ' Port is ' + str(crawler.port))

	# first round to see how switches and routers are connected
	for host in crawler.host_list:
		if not host.visited:
			crawler.get_info(host)

	crawler.print_hosts()

	crawler.generate_xml()
	crawler.generate_json()

	draw_net = drawnetwork.DrawNetwork()
	draw_net.draw(crawler.network)


def parse_input(args):
	"""docstring"""
	found_port = False
	found_address = False
	found_community = False
	debug_mode = False

	for arg in args:
		if(arg == args[0]):
			continue
		if(arg[0:2] == 'p='):
			found_port = True
			port = int(arg[2:])
		if(arg[0:2] == 'a='):
			found_address = True
			address = str(arg[2:])
		if(arg[0:2] == 'c='):
			found_community = True
			community = str(arg[2:])
		if(arg[0:1] == 'd'):
			debug_mode = True

	if(not found_address):
		kill('Must provide an address')
	if(not found_port):
		port = 161
		print('No port argument found, using default port 161')
	if(not found_community):
		community = 'public'
		print('Default community set to public')

	return address, port, community, debug_mode


def kill(why):
	"""Kill the program"""
	print(why)
	sys.exit(1)


if __name__ == "__main__":
	main()