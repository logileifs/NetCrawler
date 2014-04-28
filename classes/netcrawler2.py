"""This program crawls a network and maps it"""

from snmpwrapper import SNMPWrapper
from pingsweep import PingSweep
from dicttoxml import dicttoxml
from subnet import Subnet
from vlan import VLAN
from host import Host
from oid import OID
import ipcalc
import json
import sys

class NetCrawler:

	oid = OID()
	snmp = SNMPWrapper()

	def __init__(self, args):

		self.start_address = args[0]
		NetCrawler.snmp.community_str = args[1]
		self.port = args[2]

		self.current_subnet = None
		self.subnets = []
		self.arp_cache = {}
	

	def initialize(self):
		"""Get required information from first host to start crawling"""

		self.current_subnet = self.get_current_subnet(self.start_address)
		print('current subnet: ' + str(self.current_subnet))

		host = Host()
		host.ip = self.start_address

		self.current_subnet.host_list.append(host)


	def get_current_subnet(self, address):

		subnet = None
		results = NetCrawler.snmp.walk(self.start_address, '1.3.6.1.2.1.4.20.1.3')

		if results is not None:
			for result in results:
				for name,val in result:
					tmp = ''
					ip = str(name).split('1.3.6.1.2.1.4.20.1.3.', 1)[1]

					for char in str(val):
						tmp += str(int(char.encode('hex'),16)) + '.'

					mask = tmp[:-1]
					del tmp

					net = ipcalc.Network(ip + '/' + mask)

					if net.in_network(self.start_address):
						subnet = Subnet(net)
						self.add_subnet(subnet)
						print('FOUND SUBNET')

		return subnet


	def get_subnets(self, host):

		subnet = None
		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.4.20.1.3')

		if results is not None:
			for result in results:
				for name,val in result:
					tmp = ''
					ip = str(name).split('1.3.6.1.2.1.4.20.1.3.', 1)[1]

					for char in str(val):
						tmp += str(int(char.encode('hex'),16)) + '.'

					mask = tmp[:-1]
					del tmp

					net = ipcalc.Network(ip + '/' + mask)

					subnet = Subnet(net)
					self.add_subnet(subnet)

		#return subnet


	def add_to_host_list(self, host):


		self.current_subnet.host_list.append(host)


	"""def add_to_known_hosts(self, host):
		
		self.current_subnet.known_hosts.append(host)

		#del self.current_subnet.unknown_hosts[self.current_subnet.unknown_hosts.index(host)]"""


	def crawl(self):

		for host in self.current_subnet.host_list:
			print('Crawling ' + str(host.ip))
			
			if not host.visited:
				self.get_serial_number(host)
				
				if host.responds:
					self.get_info(host)
					

		print('\nCrawl finished\n')
		print('Known hosts:')
		for host in self.current_subnet.host_list:
			if host.visited:
				print(host.ip)

		print('\nUnknown hosts:')
		for host in self.current_subnet.host_list:
			if not host.visited:
				print(host.ip)

		print('')
		self.print_hosts()
		self.print_arp_cache()


	def get_info(self, host):

		host.interface = self.get_interface(host)
		host.mac = self.get_mac(host)
		host.name = self.get_hostname(host)
		self.get_arp_cache(host)
		self.get_subnets(host)
		self.get_if_list(host)
		self.get_ips(host)
		
		host.visited = True


	def get_serial_number(self, host):

		result = NetCrawler.snmp.get(host.ip, NetCrawler.oid.serial_number)

		if result is not None:
			for name,val in result:
				host.serial_number = str(val)
				host.responds = True
				print(str(name) + ' = ' + str(val))

		else: host.responds = False


	def add_subnet(self, subnet):

		if not self.subnet_exists(subnet):
			self.subnets.append(subnet)


	def subnet_exists(self, subnet):
		"""Return true if subnet exists otherwise false"""

		print('number of subnets: ' + str(len(self.subnets)))

		for s in self.subnets:
			if s.broadcast == subnet.broadcast \
				and s.network == subnet.network:
				print('SUBNET EXISTS')
				return True
				break

		return False


	def in_current_subnet(self, address):
		"""Return true if address belongs to current subnet otherwise false"""

		if self.current_subnet.in_network(address):
			return True
		else:
			return False


	def address_in_subnet(self, net, address):

		if net.in_network(address):
			return True
		else:
			return False


	def get_interface(self, host):
		"""Get the interface of the device"""

		#self.db_print('interface for host ', host.name)
		print('Get interface for host ' + str(host.ip))

		ip_found = False
		interface = ''

		results = NetCrawler.snmp.walk(host.ip, self.oid.interface)

		if results is None:	# catch error
			return 0

		for result in results:
			for name, val in result:

				ip_found = self.search_string_for_ip(name, host)
				if ip_found:
					print('interface of host is: ' + str(val))
					interface = int(val)
				#self.db_print(name.prettyPrint())

		return interface


	def get_mac(self, host):
		"""Get host's MAC address"""

		print('Getting MAC address')
		mac = ''

		result = NetCrawler.snmp.get(host.ip, self.oid.mac + '.' + str(host.interface))

		if result is not None:
			for name, val in result:
				mac = hex_to_mac(val)
			
		return mac


	def search_string_for_ip(self, name, host):
		"""Search for the host's ip in the snmp response"""

		ip_found = ''
		if(str(name).find(self.oid.interface + '.') != -1):
			ip_found = str(name)[21:]
			if ip_found == host.ip:
				return True

		return False


	def get_arp_cache(self, host):
		"""Get ARP table from host"""
		print('Get ARP table from host ' + str(host.ip))

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.4.22.1.2')

		if results is not None:
			for result in results:
				for name, val in result:
					ip = str(name).split('.', 11)[11]
					#print('ip: ' + ip)
					mac = hex_to_mac(val)
					#print('mac: ' + mac)
					
					if self.in_current_subnet(ip):
						new_host = Host()
						new_host.ip = ip
						new_host.mac = mac
						print(ip + ' is in current subnet')
						if not self.host_exists(new_host):
							self.add_to_host_list(new_host)
							print(str(new_host.ip) + ' added to host_list')

					self.arp_cache[ip] = mac

	"""def get_arp_cache2(self, host):	
		print('Get ARP table from host ' + str(host.ip))

		#results = NetCrawler.snmp.walk(host.ip, '.1.3.6.1.2.1.4.22.1.2.' + str(host.interface))
		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.4.22.1.2')

		if results is not None:
			for result in results:
				for name, val in result:
					print(str(name) + ' = ' + hex_to_mac(val))
					#if str(name).find('1.3.6.1.2.1.4.22.1.2.' + str(host.interface)) != -1:
					if str(name).find('1.3.6.1.2.1.4.22.1.2') != -1:	
						new_host = Host()
						new_host.ip = str(name).split('1.3.6.1.2.1.4.22.1.2.' + str(host.interface) + '.',1)[1]
						print('new host ip: ' + new_host.ip)
						new_host.mac = hex_to_mac(val)
						print('new host mac: ' + new_host.mac)

						#self.add_host(new_host)
						if self.host_exists(new_host) == False:
							self.add_to_unknown_hosts(new_host)
							print('adding ' + str(new_host.ip) + ' to unknown hosts')

						self.arp_cache[new_host.ip] = new_host.mac"""


	def get_hostname(self, host):
		"""Get the name of the host"""

		print('Getting hostname')
		hostname = ''

		result = NetCrawler.snmp.get(host.ip, NetCrawler.oid.hostname)

		if result is not None:
			for name, val in result:
				hostname = str(val)
			
		return hostname


	def get_if_list2(self, host):

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.2.2')

		if results is not None:
			for result in results:
				for name,val in result:
					print(str(name) + ' = ' + str(val))


	def get_if_list(self, host):
		"""Get list of host's interfaces"""

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.2.2.1.6')

		if results is not None:
			for result in results:
				for name,val in result:
					interface = str(name).split('1.3.6.1.2.1.2.2.1.6.', 1)[1]
					mac = hex_to_mac(val)
					#print('if: ' + interface + ' mac: ' + mac)
					host.if_table[interface] = { 'mac': mac }
		
			del interface
			del mac

		del results
		
		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.2.2.1.2')

		if results is not None:
			for result in results:
				for name,val in result:
					interface = str(name).split('1.3.6.1.2.1.2.2.1.2.', 1)[1]
					descr = str(val)
					mac = host.if_table[interface]['mac']
					#print('MAC:' + mac)
					#print('if: ' + interface + ' descr: ' + descr)
					host.if_table[interface] = { 'mac': mac, 'descr': descr, 'ips': [] }

				del interface
				del mac
				del descr

		del results

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.2.2.1.8')

		if results is not None:
			for result in results:
				for name, val in result:
					interface = str(name).split('1.3.6.1.2.1.2.2.1.8.', 1)[1]
					status = str(val)
					mac = host.if_table[interface]['mac']
					descr = host.if_table[interface]['descr']

					host.if_table[interface] = { 'mac': mac, 'descr': descr, 'status': status,
												'ips': []}


	def get_ips(self, host):
		"""Get all IP addresses of host"""

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.4.20.1.2')

		if results is not None:
			for result in results:
				for name,val in result:
					ip = str(name).split('1.3.6.1.2.1.4.20.1.2.',1)[1]
					interface = str(val)
					print('ip: ' + ip + ' if: ' + str(val))
					#descr = host.if_table[interface]['descr']
					#mac = host.if_table[interface]['mac']
					#status = host.if_table[interface]['status']
					host.if_table[interface]['ips'].append(ip)

		from pprint import pprint
		pprint(vars(host))


	def host_exists(self, host):

		for h in self.current_subnet.host_list:
			if h.ip == host.ip:
				return True
			if h.mac == host.mac:
				return True

		return False


	def print_hosts(self):

		for net in self.subnets:
			print('Subnet ' + str(net.id))
			for i,host in enumerate(net.host_list):
				print('\tHost ' + str(i))
				print('\tIP: ' + str(host.ip))
				print('\tMAC: ' + str(host.mac))
				print('\tSerial: ' + str(host.serial_number))
				print('')


	def print_arp_cache(self):

		print('ARP cache:')
		for name, val in self.arp_cache.items():
			print(name + ' = ' + val)


	def generate_json(self):
		"""docstring"""
		temp_network = self.parse_dict_for_json()
		with open('network.json', 'w') as my_file:
			json.dump(temp_network, my_file)


	def parse_dict_for_json(self):
		"""docstring"""

		network = {}
		"""self.network[host.id] = { 'mac': host.mac, 'name': host.name,
								  'ip': host.ip, 'interface': host.interface,
								  'neighbors': host.neighbors }"""

		for net in self.subnets:
			for i,host in enumerate(net.host_list):
				network['host'+str(i)] = { 'mac': host.mac, 'name': host.name,
											'ip': host.ip, 'interface': host.interface, 
											'subnet': net.id }

		for key, value in network.iteritems():
			print(key, value)
			#for neighbor in self.network[key]['neighbors']:
				#print(neighbor)

		temp_network = { 'nodes': []}

		for key in network:
			temp = network[key]
			temp['id'] = key
			temp_network['nodes'].append(temp)

		links = self.make_links(temp_network)
		temp_network['links'] = links

		return temp_network


	def make_links(self, nodes):
		"""docstring""" 
		node_list = nodes['nodes']
		links = []

		for node in node_list:
			neighbors = node['neighbors']
			if neighbors:
				source = node_list.index(node)
				for neighbor in neighbors:
					for n in node_list:
						if neighbor in n.values():
							link = {'source' : source, 'target' : node_list.index(n)}
							links.append(link)

		for link in links:
			source = link['source']
			target = link['target']
			for l in links:
				if target == l['source'] and source == l['target']:
					del links[links.index(l)]

		return links


def hex_to_mac(hexNum):

	if hexNum == '':
		return ''

	else:
		numbers = str(hexNum.asNumbers())
		numbers = numbers.replace('(', '').replace(')', '').replace(',', '')
		numList = numbers.split(' ')
		
		del numbers
		numbers = ''
		
		for num in numList:
			numbers += str(hex(int(num))[2:].zfill(2))
		
		return numbers


def parse_input(args):
	"""docstring"""
	found_port = False
	found_address = False
	found_community = False
	debug_mode = False
	#subnet = None

	for arg in args:
		if(arg == args[0]):
			continue
		if(arg[0:2] == 'p='):
			found_port = True
			port = int(arg[2:])
		if(arg[0:2] == 'a='):
			found_address = True
			#if str(arg).find('/') != -1:
				#address = str(arg[2:-3])
				#subnet = str(arg[2:])
			#else:
			address = str(arg[2:])
			print('address: ' + address)
		if(arg[0:2] == 'c='):
			found_community = True
			community = str(arg[2:])
		#if(arg[0:1] == 'd'):
			#debug_mode = True

	if(not found_address):
		kill('Must provide an address')
	if(not found_port):
		port = 161
		print('No port argument found, using default port 161')
	if(not found_community):
		community = 'public'
		print('Default community set to public')

	arguments = [address, community, port]
	return arguments


def kill(why):
	"""Kill the program"""
	print(why)
	sys.exit(1)


def main():
	"""Main function to invoke the NetCrawler"""

	arguments = parse_input(sys.argv)
	crawler = NetCrawler(arguments)

	crawler.initialize()
	crawler.crawl()

	#crawler.print_hosts()

	#crawler.generate_xml()
	#crawler.generate_json()

	#draw_net = drawnetwork.DrawNetwork()
	#draw_net.draw(crawler.network)


if __name__ == '__main__':
	main()