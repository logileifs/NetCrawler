"""This program crawls a network and maps it"""

from snmpwrapper import SNMPWrapper
from pingsweep import PingSweep
from dicttoxml import dicttoxml
from interface import Interface
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
		host.model = self.get_model(host)
		self.get_arp_cache(host)
		self.get_subnets(host)
		self.get_if_list(host)
		self.get_ips(host)

		self.get_type(host)

		if host.is_switch():
			host.if_descr = self.get_if_descr(host)
			host.ent_table_nr = self.get_ent_table_nr(host)
			host.vlan_id = self.get_vlan_id(host)
			self.get_if_on_vlan(host)
			self.get_port_list(host)

		elif host.is_router():
			self.get_if_of_ip(host)
		
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
		else: return False


	def get_interface(self, host):
		"""Get the interface of the device on this subnet"""

		print('Get interface for host ' + str(host.ip))

		ip_found = False
		interface = None

		results = NetCrawler.snmp.walk(host.ip, self.oid.interface)

		if results is not None:
			for result in results:
				for name, val in result:
					ip_found = self.search_string_for_ip(name, host)
					if ip_found:
						print('interface of host is: ' + str(val))
						interface = int(val)
					#print(name.prettyPrint())

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


	def get_hostname(self, host):
		"""Get the name of the host"""

		print('Getting hostname')
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
				for name,val in result:
					interface = str(name).split('1.3.6.1.2.1.2.2.1.6.', 1)[1]
					mac = hex_to_mac(val)
					host.if_table[interface] = { 'mac': mac }

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
				for name,val in result:
					interface = str(name).split('1.3.6.1.2.1.2.2.1.2.', 1)[1]
					descr = str(val)
					mac = host.if_table[interface]['mac']
					host.if_table[interface] = { 'mac': mac, 'descr': descr, 'ips': [] }

					intf = host.get_interface(interface)
					intf.descr = descr

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

					host.if_table[interface] = { 'mac': mac, 'descr': descr,
												'status': status, 'ips': [],
												'connected': [] }

					intf = host.get_interface(interface)
					intf.status = status


	def get_if_on_vlan(self, host):
		"""dot1dBasePortIfIndex"""
		from pprint import pprint

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.17.1.4.1.2', host.vlan_id)

		if results is not None:
			for result in results:
				for name,val in result:
					port = str(name).split('1.3.6.1.2.1.17.1.4.1.2.', 1)[1]
					interface = str(val)
					#print(str(name) + ' = ' + str(val))
					#print('port ' + port + ' is on interface ' + str(val))
					host.if_table[interface]['port'] = port

					intf = host.get_interface(interface)
					intf.port = port
					#pprint(vars(intf))


	def get_ips(self, host):
		"""Get all IP addresses of host"""

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.4.20.1.2')

		if results is not None:
			for result in results:
				for name,val in result:
					ip = str(name).split('1.3.6.1.2.1.4.20.1.2.',1)[1]
					interface = str(val)
					host.if_table[interface]['ips'].append(ip)

					intf = host.get_interface(interface)
					if intf: intf.ips.append(ip)

		#from pprint import pprint
		#pprint(vars(host))


	def get_type(self, host):
		"""Check the type of the device"""

		if self.router_check(host):
			host.types.append('router')
		
		if self.switch_check(host):
			host.types.append('switch')

		#printer_check()	#this feature will be implemented later


	def router_check(self, host):
		"""Check if the device is a router"""

		print('Checking if ' + str(host.ip) + ' is a router')

		ip_forwarding = False
		if_number = 0

		result = NetCrawler.snmp.get(host.ip, self.oid.type)

		if result is not None:
			for name, val in result:
				#print(val.prettyPrint())
				if int(val) == 1:
					ip_forwarding = True

		result = NetCrawler.snmp.get(host.ip, '1.3.6.1.2.1.2.1.0')

		if result is not None:
			for name,val in result:
				if_number = int(val)
		
		if if_number >= 2 and ip_forwarding:	#router must have 2 or more interfaces
			print(str(host.ip) + ' is a router')
			return True

		else: return False


	def switch_check(self, host):
		"""Check if the device is a switch"""

		print('Checking if ' + str(host.ip) + ' is a switch')
		number_of_ports = None
		cost_to_root = None
		lowest_cost_port = None

		result = NetCrawler.snmp.get(host.ip, self.oid.num_of_ports)

		if result != None:
			for name, val in result:
				number_of_ports = int(val)
				print('number of ports: ' + str(number_of_ports))

		else: return False

		result = NetCrawler.snmp.get(host.ip, self.oid.cost_to_root)

		if result is None:
			print('result is none')

		if result != None:
			for name, val in result:
				if val.__class__.__name__ == 'NoSuchInstance':
					return False
				else:
					cost_to_root = int(val)

		else: return False

		result = NetCrawler.snmp.get(host.ip, self.oid.lowest_cost_port)

		if result != None:
			for name, val in result:
				lowest_cost_port = int(val)
				print('lowestCostPort: ' + str(lowest_cost_port))

		else: return False

		if number_of_ports != None and cost_to_root != None and lowest_cost_port != None:
			host.type = 'switch'
			return True

		else: return False


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
					#print('found @ at index ' + str(index))
					vlan_id = str(val)[index:]
					#print('vlan_id: ' + vlan_id)

		return vlan_id


	def get_port_list(self, host):
		"""Find where end devices are connected on the network"""

		port_list = {}
		neighbors = []

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.17.4.3.1.2', host.vlan_id)

		if results is not None:
			for result in results:
				for name, val in result:
					mac = dec_to_mac(str(name)[23:])
					port = str(val)
					host.if_table[str(val)]['connected'].append(mac)
					#self.add_mac_on_if(host, port, mac)
					host.port_list[dec_to_mac(str(name)[23:])] = int(val)

					intf = host.get_interface_by_port(port)
					intf.macs_connected.append(mac)

		from pprint import pprint
		pprint(vars(host))


	"""def add_mac_on_if(self, host, port, mac):

		print('adding mac ' + str(mac) + ' to interface with port ' + str(port))
		interface = None

		for name,val in host.if_table.iteritems():
			#print('name: ' + str(name) + ' val.port: ' + str(val))
			for n,v in val.iteritems():
				if n == 'port' and v == port:
					interface = name
					print('found port ' + port + ' on interface ' + interface)
					#print('port: ' + str(v))
					break

		if interface and mac not in host.if_table[interface]['connected']:
			#print('found port ' + str(port) + ' on interface ' + str(interface))
			host.if_table[interface]['connected'].append(mac)"""


	def get_if_of_ip(self, host):
		"""ipNetToMediaIfIndex"""

		print('ipNetToMediaIfIndex')

		ipNetToMediaIfIndex = {}

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.4.22.1.1')

		if results is not None:
			for result in results:
				for name,val in result:
					#print(str(name) + ' = ' + str(val))
					ip = str(name).split('.', 11)[11]
					interface = str(val)
					#print('ip: ' + ip)
					#print('interface: ' + interface)
					ipNetToMediaIfIndex[ip] = interface


		"""ipNetToMediaPhysAddress"""

		print('ipNetToMediaPhysAddress')

		ipNetToMediaPhysAddress = {}

		results = NetCrawler.snmp.walk(host.ip, '1.3.6.1.2.1.4.22.1.2')

		if results is not None:
			for result in results:
				for name,val in result:
					ip = str(name).split('.', 11)[11]
					mac = hex_to_mac(val)
					print('ip: ' + ip)
					print('mac: ' + mac)
					ipNetToMediaPhysAddress[ip] = mac

		#kill('because i said so')


	def get_model(self, host):


		model = ''
		result = NetCrawler.snmp.get(host.ip, NetCrawler.oid.model)

		if result is not None:
			for name,val in result:
				model = str(val)

		return model


	def host_exists(self, host):

		for h in self.current_subnet.host_list:
			if h.ip == host.ip:
				return True
			if h.mac == host.mac:
				return True

		return False


	def print_hosts(self):

		for net in self.subnets:
			for host in net.host_list:
				host.print_host()
				print('interfaces:')
				for interface in host.interfaces:
					interface.print_interface()
		"""for net in self.subnets:
			print('Subnet ' + str(net.id))
			for i,host in enumerate(net.host_list):
				print('\tHost ' + str(i))
				print('\tIP: ' + str(host.ip))
				print('\tMAC: ' + str(host.mac))
				print('\tInterface: ' + str(host.interface))
				print('\tSerial: ' + str(host.serial_number))
				print('\tModel: ' + str(host.model))
				print('\tif_descr: ' + str(host.if_descr))
				print('\tent_table_nr: ' + str(host.ent_table_nr))
				print('\tvlan_id: ' + str(host.vlan_id))
				print('\ttypes:')
				print(host.types)
				print('\tVisited: ' + str(host.visited))
				print('')"""


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


def dec_to_mac(dec_string):
	"""Convert decimal MAC address to hex"""

	hex_string = ''
	numbers = dec_string.split('.')

	for number in numbers:
		hex_string += str(hex(int(number))[2:].zfill(2))

	return hex_string


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