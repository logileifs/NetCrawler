"""This program crawls a network and maps it"""

from classes.snmpwrapper import SNMPWrapper
from classes.interface import Interface
from classes.subnet import Subnet
from classes.host import Host
from classes.oid import OID
import subprocess
import getopt
import ipcalc
import json
import sys
import re

class NetCrawler:
	"""NetCrawler main class"""
	#oid = OID('cisco')
	oid = None
	snmp = SNMPWrapper()

	def __init__(self, address, community, port, depth):

		self.start_address = address
		NetCrawler.snmp.community_str = community
		self.port = port
		self.depth = depth
		print('depth: ' + str(self.depth))

		self.current_subnet = None
		self.subnets = []
		self.arp_cache = {}
		self.host_counter = 0
		self.all_hosts = []

		#print('depth: ' + str(self.depth))


	def get_oid(self, vendor=''):

		NetCrawler.oid = OID(vendor)




	def initialize(self):
		"""Get required information from first host to start crawling"""

		self.get_oid()

		self.current_subnet = self.get_current_subnet(self.start_address)

		self.current_subnet.add_unknown_ip(self.start_address)

		#kill('First host did not answer SNMP')


	def create_host(self, ip_addr):
		"""Create a new host"""

		#print('CREATING NEW HOST WITH IP ' + str(ip_addr))

		if self.ip_exists(ip_addr):
			#print('\tIP ALREADY EXISTS')
			return self.get_host_by_ip(ip_addr)

		new_host = Host()
		new_host.id += str(self.host_counter)
		new_host.ip = ip_addr
		new_host.add_ip(ip_addr)

		self.host_counter += 1

		self.all_hosts.append(new_host)
		self.add_to_host_list(new_host)

		return new_host


	def add_to_host_list(self, host):
		"""Add host to list of hosts on this subnet"""

		self.current_subnet.add_host(host)


	def add_unknown_ip(self, ip_addr):

		for subnet in self.get_all_subnets():
			if self.address_in_subnet(subnet, ip_addr):
				subnet.add_unknown_ip(ip_addr)


	def get_all_subnets(self):

		all_subnets = []

		for subnet in self.subnets:
			all_subnets.append(subnet)

		return all_subnets


	def get_current_subnet(self, address):
		"""Get the current subnet of this address"""

		subnet = None
		results = NetCrawler.snmp.walk(address, '1.3.6.1.2.1.4.20.1.3')

		if results is not None:
			for result in results:
				for name, val in result:
					tmp = ''
					ip_addr = str(name).split('1.3.6.1.2.1.4.20.1.3.', 1)[1]

					for char in str(val):
						tmp += str(int(char.encode('hex'), 16)) + '.'

					mask = tmp[:-1]
					del tmp

					net = ipcalc.Network(ip_addr + '/' + mask)

					if net.in_network(address):
						subnet = Subnet(net)
						self.add_subnet(subnet)

		return subnet


	def get_subnets(self, host):
		"""Get all the subnets that this host is aware of"""

		subnet = None
		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.4.20.1.3')

		if results is not None:
			for result in results:
				for name, val in result:
					tmp = ''
					ip_addr = str(name).split('1.3.6.1.2.1.4.20.1.3.', 1)[1]

					for char in str(val):
						tmp += str(int(char.encode('hex'), 16)) + '.'

					mask = tmp[:-1]
					del tmp

					net = ipcalc.Network(ip_addr + '/' + mask)

					subnet = Subnet(net)
					self.add_subnet(subnet)


	def snmp_ping(self, host):

		result = NetCrawler.snmp.get(host.ip, self.oid.sys_descr)

		if result is not None:
			host.responds = True
			# Here should the vendor of the device be known
			# host.vendor = ''
			return True
		else:
			host.responds = False
			return False


	def get_next_subnet(self):

		for subnet in self.subnets:
			if subnet.scanned == False:
				return subnet


	def crawl(self):
		"""NetCrawler main loop"""

		for i, subnet in enumerate(self.subnets):
			if i >= self.depth and self.depth != 0:
				print('MAXIMUM DEPTH REACHED')
				break
			print('SCANNING SUBNET ' + str(subnet.id))
			while self.current_subnet.unknown_ips:

				ip_addr = self.current_subnet.get_next_unknown_ip()

				print('CRAWLING ' + str(ip_addr))

				new_host = self.create_host(ip_addr)
				if self.snmp_ping(new_host):
					new_host.responds = True
					self.get_oid(new_host.vendor)
					self.get_info(new_host)
				else:
					new_host.responds = False
					new_host.type = 'end_device'
					"""If host doesn't answer snmp"""
					"""get mac address from arp cache"""
					new_host.mac = self.arp_cache[ip_addr]
					new_host.add_mac(new_host.mac)

				self.current_subnet.add_known_ip(ip_addr)
				self.current_subnet.remove_unknown_ip(ip_addr)

			self.track_ports()
			
			for host in self.current_subnet.host_list:
				if host.responds:
					self.get_neighbors(host)

			self.current_subnet.scanned = True
			print('SUBNET ' + str(self.current_subnet.id) + ' SCANNED')

			self.current_subnet = self.get_next_subnet()

		self.print_results()


	def get_info(self, host):
		"""Wrapper function to call all relevant get functions"""

		host.interface = self.get_interface(host)
		host.mac = self.get_mac(host)
		host.name = self.get_hostname(host)
		host.model = self.get_model(host)
		host.serial_number = self.get_serial_number(host)
		self.get_subnets(host)
		self.get_if_list(host)
		self.get_ips(host)
		self.get_arp_cache(host)

		self.get_type(host)

		if host.is_switch():
			host.if_descr = self.get_if_descr(host)
			host.ent_table_nr = self.get_ent_table_nr(host)
			host.vlan_id = self.get_vlan_id(host)
			self.get_if_on_vlan(host)
			self.get_port_list(host)

		if host.is_router():
			self.get_macs_on_interface(host)
		
		host.visited = True


	def get_serial_number(self, host):
		"""Get serial number of host"""

		serial_number = ''

		result = NetCrawler.snmp.get(host.ip, NetCrawler.oid.serial_number)

		if result is not None:
			for name, val in result:
				serial_number = str(val)
				#host.serial_number = str(val)
				#host.responds = True
				#print(str(name) + ' = ' + str(val))

		return serial_number
		#else: host.responds = False


	def add_subnet(self, subnet):
		"""Add new subnet to subnet list"""

		if not self.subnet_exists(subnet):
			self.subnets.append(subnet)


	def subnet_exists(self, subnet):
		"""Return true if subnet exists otherwise false"""

		#print('number of subnets: ' + str(len(self.subnets)))

		for net in self.subnets:
			if net.broadcast == subnet.broadcast:
				if net.network == subnet.network:
					#print('SUBNET EXISTS')
					return True
					#break

		return False


	def in_current_subnet(self, address):
		"""Return true if address belongs to current subnet otherwise false"""

		if self.current_subnet.in_network(address):
			return True
		else:
			return False


	def address_in_subnet(self, subnet, address):
		"""Return true if address is in this subnet's range"""

		if subnet.in_network(address):
			return True
		else: return False


	def get_interface(self, host):
		"""Get the interface of the device on this subnet"""

		#print('Get interface for host ' + str(host.ip))

		ip_found = False
		interface = None

		results = NetCrawler.snmp.walk(host.ip, self.oid.interface)

		if results is not None:
			for result in results:
				for name, val in result:
					ip_addr = str(name).split(self.oid.interface + '.', 1)[1]
					if ip_addr == host.ip:
						interface = int(val)

		return interface


	def get_mac(self, host):
		"""Get host's MAC address"""

		#print('Getting MAC address')
		mac = ''

		result = NetCrawler.snmp.get(host.ip, self.oid.mac + '.' + str(host.interface))

		if result is not None:
			for name, val in result:
				mac = hex_to_mac(val)
			
		return mac


	def get_arp_cache(self, host):
		"""Get ARP table from host"""
		#print('Get ARP table from host ' + str(host.ip))

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.4.22.1.2')

		if results is not None:
			for result in results:
				for name, val in result:
					ip_addr = str(name).split('.', 11)[11]
					mac = hex_to_mac(val)
					
					self.add_unknown_ip(ip_addr)
					self.arp_cache[ip_addr] = mac


	def get_neighbors(self, host):
		"""Get the neighbors of this host using Cisco Discovery Protocol"""

		#print('GETTING NEIGHBORS FOR ' + str(host.ip))
		results = NetCrawler.snmp.walk(host.ip, NetCrawler.oid.neighbors)

		if results is not None:
			for result in results:
				for name, val in result:
					ip_addr = hex_to_ip(val)
					#print('neighbor: ' + str(ip))
					neighbor = self.get_host_by_ip(ip_addr)

					if neighbor:
						#print('neighbor mac: ' + str(neighbor.mac))
						intf = host.get_interface_by_mac(neighbor.mac)
						#print('ADDING NEIGHBOR ' + neighbor.ip + ' to host ' + host.ip)
						#print('ADDING NEIGHBOR ' + neighbor.mac + ' to host ' + host.mac)
						host.add_neighbor(neighbor.id)
						try:
							host.add_connection(neighbor.id, intf.name)
						except AttributeError:
							host.add_connection(neighbor.id, 'unknown')
							#print("neighbor: " + neighbor.id + ' host: ' + host.id)
							#print('neighbor mac: ' + neighbor.mac + ' host mac: ' + host.mac)
							#print('host:')
							#host.print_host()
							#host.print_interfaces()
							#print('neighbor:')
							#neighbor.print_host()
							#neighbor.print_interfaces()
							#kill('error')
						#print(neighbor.ip + ' is neighbor of ' + str(host.ip))
						#print('the neighbor is on interface ' + intf.descr)


	def get_hostname(self, host):
		"""Get the name of the host"""

		#print('Getting hostname')
		hostname = ''

		result = NetCrawler.snmp.get(host.ip, NetCrawler.oid.hostname)

		if result is not None:
			for name, val in result:
				hostname = str(val)
			
		return hostname


	def get_if_list(self, host):
		"""Get list of host's interfaces"""

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.2.2.1.6')

		if results is not None:
			for result in results:
				for name, val in result:
					interface = str(name).split('1.3.6.1.2.1.2.2.1.6.', 1)[1]
					mac = hex_to_mac(val)

					host.add_mac(mac)

					intf = Interface()
					intf.number = str(name).split('1.3.6.1.2.1.2.2.1.6.', 1)[1]
					intf.mac = hex_to_mac(val)
					host.add_interface(intf)
		
			del interface
			del mac

		del results
		
		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.2.2.1.2')

		if results is not None:
			for result in results:
				for name, val in result:
					interface = str(name).split('1.3.6.1.2.1.2.2.1.2.', 1)[1]
					descr = str(val)

					intf = host.get_interface(interface)
					intf.descr = descr

				del interface
				del descr

		del results

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.2.2.1.8')

		if results is not None:
			for result in results:
				for name, val in result:
					interface = str(name).split('1.3.6.1.2.1.2.2.1.8.', 1)[1]
					status = str(val)

					intf = host.get_interface(interface)
					intf.status = status

		del results
		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.31.1.1.1.1')

		#print('ifName')
		if results is not None:
			for result in results:
				for name, val in result:
					interface = str(name).split('1.3.6.1.2.1.31.1.1.1.1.', 1)[1]
					if_name = str(val)

					intf = host.get_interface(interface)
					intf.name = if_name


	def get_if_on_vlan(self, host):
		"""dot1dBasePortIfIndex"""

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.17.1.4.1.2', host.vlan_id)

		if results is not None:
			for result in results:
				for name, val in result:
					port = str(name).split('1.3.6.1.2.1.17.1.4.1.2.', 1)[1]
					interface = str(val)

					intf = host.get_interface(interface)
					intf.port = port


	def get_ips(self, host):
		"""Get all IP addresses of host"""

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.4.20.1.2')

		if results is not None:
			for result in results:
				for name, val in result:
					ip_addr = str(name).split('1.3.6.1.2.1.4.20.1.2.', 1)[1]
					interface = str(val)

					host.add_ip(ip_addr)

					self.current_subnet.add_known_ip(ip_addr)
					self.current_subnet.remove_unknown_ip(ip_addr)

					intf = host.get_interface(interface)
					
					if intf:
						intf.ips.append(ip_addr)


	def get_type(self, host):
		"""Check the type of the device"""

		if self.router_check(host):
			host.add_type('router')
			host.type = 'networking'
		
		if self.switch_check(host):
			host.add_type('switch')
			host.type = 'networking'


		#printer_check()	#this feature will be implemented later


	def router_check(self, host):
		"""Check if the device is a router"""

		ip_forwarding = False
		if_number = 0

		result = NetCrawler.snmp.get(host.ip, self.oid.type)

		if result is not None:
			for name, val in result:
				if int(val) == 1:
					ip_forwarding = True

		result = NetCrawler.snmp.get(host.ip, '1.3.6.1.2.1.2.1.0')

		if result is not None:
			for name, val in result:
				if_number = int(val)
		
		if if_number >= 2 and ip_forwarding:	#router must have 2 or more interfaces
			return True
		else:
			return False


	def switch_check(self, host):
		"""Check if the device is a switch"""

		number_of_ports = None
		cost_to_root = None
		lowest_cost_port = None

		result = NetCrawler.snmp.get(host.ip, self.oid.num_of_ports)

		if result is not None:
			for name, val in result:
				if val.__class__.__name__ == 'NoSuchInstance'\
				or val.__class__.__name__ == 'NoSuchObject':
					return False
				else:
					number_of_ports = int(val)

		else: return False

		result = NetCrawler.snmp.get(host.ip, self.oid.cost_to_root)

		if result is not None:
			for name, val in result:
				if val.__class__.__name__ == 'NoSuchInstance':
					return False
				else:
					cost_to_root = int(val)

		else: return False

		result = NetCrawler.snmp.get(host.ip, self.oid.lowest_cost_port)

		if result is not None:
			for name, val in result:
				lowest_cost_port = int(val)

		else: return False

		if number_of_ports is not None:
			if cost_to_root is not None:
				if lowest_cost_port is not None:
					host.type = 'switch'
					return True

		return False


	def get_if_descr(self, host):
		"""Get the description of the interface"""

		if_descr = ''

		result = NetCrawler.snmp.get(host.ip, '1.3.6.1.2.1.2.2.1.2.' + str(host.interface))

		if result is not None:
			for name, val in result:
				if_descr = str(val)

		return if_descr


	def get_ent_table_nr(self, host):
		"""Get the correct place of vlan id in entLogicalDescr table"""

		ent_table_nr = None

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.47.1.2.1.1.2')

		if results is not None:
			for result in results:
				for name, val in result:
					if str(val) == host.if_descr.lower():
						ent_table_nr = str(name)[-1]

		return ent_table_nr


	def get_vlan_id(self, host):
		"""Get the vlan id from entLogicalDescr table"""

		if host.ent_table_nr is None:
			return ''

		vlan_id = ''

		result = NetCrawler.snmp.get(host.ip, '1.3.6.1.2.1.47.1.2.1.1.4.' + str(host.ent_table_nr))

		if result is not None:
			for name, val in result:
				index = str(val).find('@')
				if index != -1:
					vlan_id = str(val)[index:]

		return vlan_id


	def get_port_list(self, host):
		"""Find where end devices are connected on the network"""

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.17.4.3.1.2', host.vlan_id)

		if results is not None:
			for result in results:
				for name, val in result:
					mac = dec_to_mac(str(name)[23:])
					port = str(val)

					intf = host.get_interface_by_port(port)
					
					if intf:
						intf.macs_connected.append(mac)


	def get_macs_on_interface(self, host):
		"""ipNetToMediaIfIndex"""

		#if host.ip == '192.168.60.254':
			#print('GETTING MACS ON INTERFACE FOR HOST ' + host.ip)

		#ipNetToMediaIfIndex = {}
		ip_to_interface = {}

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.4.22.1.1')

		if results is not None:
			for result in results:
				for name, val in result:
					ip_addr = str(name).split('.', 11)[11]
					interface = str(val)
					
					#ipNetToMediaIfIndex[ip_addr] = interface
					ip_to_interface[ip_addr] = interface


		"""ipNetToMediaPhysAddress"""


		#ipNetToMediaPhysAddress = {}
		ip_to_mac =  {}

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.4.22.1.2')

		if results is not None:
			for result in results:
				for name, val in result:
					ip_addr = str(name).split('.', 11)[11]
					mac = hex_to_mac(val)
					
					#ipNetToMediaPhysAddress[ip_addr] = mac
					ip_to_mac[ip_addr] = mac

					#interface = ipNetToMediaIfIndex[ip_addr]
					interface = ip_to_interface[ip_addr]

					intf = host.get_interface(interface)
					intf.macs_connected.append(mac)


	def get_model(self, host):
		"""docstring"""

		model = ''
		result = NetCrawler.snmp.get(host.ip, NetCrawler.oid.model)

		if result is not None:
			for name, val in result:
				model = str(val)

		return model


	def get_all_hosts(self):
		"""docstring"""

		all_hosts = []
		for subnet in self.subnets:
			for host in subnet.host_list:
				all_hosts.append(host)

		return all_hosts


	def host_exists(self, new_host):
		"""docstring"""

		for host in self.current_subnet.host_list:
			if host.ip == new_host.ip:
				return True
			if host.mac == new_host.mac:
				return True

		return False


	def get_host_by_ip(self, ip_addr):
		"""docstring"""

		for host in self.get_all_hosts():
			if ip_addr in host.ips:
				return host

		return None


	def get_host_by_mac(self, mac_addr):
		"""docstring"""

		for host in self.current_subnet.host_list:
			if mac_addr in host.macs:
				return host
			if mac_addr == host.mac:
				return host

		return None


	def ip_exists(self, ip_addr):
		"""docstring"""

		if self.get_host_by_ip(ip_addr) is not None:
			return True
		else:
			return False


	def mac_exists(self, mac):
		"""docstring"""

		if self.get_host_by_mac(mac) is not None:
			return True
		else:
			return False


	def track_ports(self):
		"""docstring"""

		for host in self.current_subnet.host_list:
			#print('check ports of ' + str(host.ip))
			for intf in host.interfaces:
				if intf.has_connections():
					if intf.number_of_connections() == 1:
						mac = intf.macs_connected[0]
						neighbor = self.get_host_by_mac(mac)

						host.add_neighbor(neighbor.id)
						host.add_connection(neighbor.id, intf.name)

						#neighbor.add_neighbor(host.id)
						#neighbor.add_connection(host.id, intf.name)

						print(str(intf.macs_connected[0]) + ' is neighbor of ' + str(host.ip))
						print(str(host.id) + ' has ' + str(neighbor.id) + ' on interface ' + intf.name)


	def print_hosts(self):
		"""docstring"""

		for net in self.subnets:
			print('in subnet ' + str(net.id))
			for host in net.host_list:
				print('')
				host.print_host()
				print('connections:')
				for connection in host.connections:
					print(connection[0] + ' on port ' + connection[1])
				#print('interfaces:')
				#host.print_interfaces()


	def print_results(self):

		print('\nCRAWL FINISHED')
		print('------------------------------')
		print('FOUND ' + str(len(self.subnets)) + ' SUBNETS')
		print('AND ' + str(len(self.get_all_hosts())) + ' HOSTS')
		print('------------------------------')

		for subnet in self.subnets:
			print(str(len(subnet.host_list)) + ' HOST(S) IN SUBNET ' + str(subnet.id) + '\n')
			for host in subnet.host_list:
				host.print_host()
				print('')


	def print_arp_cache(self):
		"""docstring"""

		print('ARP cache:')
		for name, val in self.arp_cache.items():
			print(name + ' = ' + val)


	def generate_json(self):
		"""docstring"""

		temp_network = self.parse_dict_for_json()
		with open('draw/net.json', 'w') as my_file:
			json.dump(temp_network, my_file)


	def parse_dict_for_json(self):
		"""docstring"""

		network = {}

		for net in self.subnets:
			for host in net.host_list:
				network[host.id] = { 'mac': host.mac, 'name': host.name,
											'ip': host.ip, 'visited': host.visited, 
											'type': host.type, 'types': host.types,
											'visited': host.visited, 'ips': host.ips,
											'serial': host.serial_number,
											'neighbors': host.neighbors, 'macs': host.macs,
											'connections': host.connections }

		#for key,val in network.iteritems():
			#print(key, val)

		temp_network = { 'nodes': [] }

		for key in network:
			temp = network[key]
			temp['id'] = key
			temp_network['nodes'].append(temp)

		links = self.make_links(temp_network)
		temp_network['links'] = links

		for key, val in network.iteritems():
			print(key, val)

		return temp_network


	def make_links(self, nodes):
		"""docstring""" 

		node_list = nodes['nodes']
		links = []

		host_to_index = {}
		for node in node_list:
			source = node_list.index(node)
			host_to_index[node['id']] = node_list.index(node)
			print(node['id'])
			print('source: ' + str(source))
			#for connection in node['connections']:
				#print(connection)
				#target = node_list.index()
		print(host_to_index)

		print('ALL CONNECTIONS:')
		for host in self.get_all_hosts():
			for connection in host.connections:
				print(host.id + ' has connection:')
				print(connection)
				link = { 'source': host.id, 'target': connection[0], 'sport': connection[1] }
				links.append(link)

		for link in links:
			#print(link)
			for link2 in links:
				if link['source'] == link2['target'] and link['target'] == link2['source']:
					link['tport'] = link2['sport']

		for link in links:
			link['source'] = host_to_index[link['source']]
			link['target'] = host_to_index[link['target']]
			if 'tport' not in link.keys():
				link['tport'] = 'unknown'
			print(link)

		# Eliminate double connections
		for link1 in links:
			for link2 in links:
				if link1['source'] == link2['target']:
					if link1['target'] == link2['source']:
						if link1['sport'] == link2['tport']:
							if link1['tport'] == link2['sport']:
								print('delete link')
								print(link1)
								links.remove(link1)

		print('')
		for link in links:
			print(link)


		return links


def hex_to_mac(hex_num):
	"""docstring"""

	if hex_num == '':
		return ''

	else:
		numbers = str(hex_num.asNumbers())
		numbers = numbers.replace('(', '').replace(')', '').replace(',', '')
		num_list = numbers.split(' ')
		
		del numbers
		numbers = ''
		
		for num in num_list:
			numbers += str(hex(int(num))[2:].zfill(2))
		
		return numbers


def hex_to_ip(hex_num):
	"""docstring"""

	numbers = str(hex_num.asNumbers())
	octet = numbers.replace('(', '').replace(')', '').replace(' ', '').replace(',', '.')
	return octet


def dec_to_mac(dec_string):
	"""Convert decimal MAC address to hex"""

	hex_string = ''
	numbers = dec_string.split('.')

	for number in numbers:
		hex_string += str(hex(int(number))[2:].zfill(2))

	return hex_string


def kill(why):
	"""Kill the program"""

	print(why)
	sys.exit(1)


def print_help():

	print('')
	print('Welcome to Men&Mice NetCrawler' )
	print('Usage: netcrawler.py -a <address> [-c <community>]' )
	print('			[-d <depth>]')
	print('                  [-l <file>][--log=<file>]' )
	print('                  [--debug]' )
	print('                  [-h][--help]' )
	print('Example: python netcrawler.py -a 192.168.60.254 -c public -d 3')
	#print('')


def parse_arguments(opts, extraparams):

	# initialized data
	address = None
	community = 'public'
	port = 161
	depth = 0

	for o, p in opts:
		if o == '-a':
			address = p
			result = re.match('^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$', address)
			if result is None:
				raise Exception('Invalid ip address')
		elif o == '-c':
			community = p
		elif o == '-d':
			depth = int(p)
		elif o == '-p':
			port = p
		#elif o in ('-b', 'debug'):
			#logging.getLogger().setLevel(logging.DEBUG)
		#elif o in ('-l', '--log'):
			#hdlr = logging.FileHandler(p)			
		elif o in ('-h', '--help'):
			print_help()
			kill('Help printed')

	if not address:
		raise Exception('No address argument')

	return address, community, port, depth


def main():
	"""Main function to invoke the NetCrawler"""

	# set up logger
	"""tmpLog = logging.getLogger(__name__)
	hdlr = logging.StreamHandler(sys.stderr)
	logging.getLogger().setLevel(logging.WARNING)"""
	

	opts, extraparams = getopt.getopt(sys.argv[1:], 'hbl:a:c:p:d:',['debug', 'log=', 'help'])
	
	try:
		address, community, port, depth = parse_arguments(opts, extraparams)
	except Exception, msg:
		print_help()
		kill(msg)

	crawler = NetCrawler(address, community, port, depth)
	crawler.initialize()
	crawler.crawl()
	crawler.generate_json()
	subprocess.call('./startinbrowser.sh')

if __name__ == '__main__':
	main()