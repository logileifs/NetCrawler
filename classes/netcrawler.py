"""This program crawls a network and maps it"""

from pysnmp.entity.rfc3413.oneliner import cmdgen
from pingsweep import PingSweep
from dicttoxml import dicttoxml
from vlan import VLAN
from host import Host
from oid import OID
import ipcalc
import json
import sys

class Crawler:
	"""This is the main class"""

	oid = OID()
	pingsweep = PingSweep()

	def __init__(self, args):
		"""Crawler constructor, takes port and address as arguments"""

		self.subnet = args[0]					# starting point
		self.community_str = args[1]
		self.port = args[2]
		self.debug_mode = args[3]
		self.cmd_gen = cmdgen.CommandGenerator()
		self.host_list = []
		self.network = {}
		self.subnets = {}
		self.range = []
		self.hosts = []
		self.vlans = []


	def initialize(self):
		address_range = self.get_address_range(self.subnet)
		print('Size of network: ' + str(address_range.size()))
		self.alive_hosts = self.get_alive_hosts(address_range)

		for counter, ip in enumerate(self.alive_hosts):
			host = Host()
			host.ip = ip
			host.id += str(counter)
			self.host_list.append(host)


	def crawl(self):
		"""Start crawling the network"""
		for host in self.host_list:
			if not host.visited:
				self.get_info(host)

		for host in self.host_list:
			for name, val in host.port_list.iteritems():
				if mac_exists(name):
					print(name + ' exists')
				else:
					print(name + ' does not exist')


	def mac_exists(self, mac):
		"""Check if a given MAC address exists in the list of hosts"""

		for host in self.host_list:
			if host.mac == mac:
				return True

		return False


	def get_address_range(self, subnet):
		"""Calculate and return subnet range"""
		
		address_range = ipcalc.Network(subnet)

		return address_range


	def get_alive_hosts(self, address_range):
		"""Execute pingsweep and return all alive hosts"""
		
		alive_hosts = []
		alive_hosts = self.pingsweep.sweep(address_range)

		return alive_hosts


	def get_error(self, indication, status, index, address):
		"""SNMP GET error handler"""
		
		print('SNMPGET ERROR')

		if indication:
			print(str(indication) + ' from ' + str(address))
		elif status:
			print(status)


	def walk_error(self, indication, status, index, address, var_bind_table):
		"""SNMP WALK error handler"""

		print('SNMPWALK ERROR')

		if indication:
			print(str(indication) + ' from ' + str(address))
		else:
			if status:
				print('%s at %s' % (status.prettyPrint(), index
				and var_bind_table[-1][int(index)-1] or '?'))


	def get(self, address, oid):
		"""docstring"""

		error_indication, error_status, error_index, var_binds = self.cmd_gen.getCmd(
			cmdgen.CommunityData(self.community_str),
			cmdgen.UdpTransportTarget((address, self.port)),
			cmdgen.MibVariable(oid),
			lookupNames=True, lookupValues=True
		)

		# Check for errors
		if error_indication or error_status:
			self.get_error(error_indication, error_status, error_index, address)
		else:
			return var_binds


	def walk2(self, address, oid, vlan_id):
		"""docstring"""

		error_indication, error_status, error_index, var_bind_table = self.cmd_gen.nextCmd(
			cmdgen.CommunityData(vlan_id),
			cmdgen.UdpTransportTarget((address, self.port)),
			oid
		)

		# Check for errors
		if error_indication or error_status:
			self.walk_error(error_indication, error_status, error_index, address, var_bind_table)
		else:
			return var_bind_table


	def walk(self, address, oid):
		"""docstring"""

		err_indication, err_status, err_index, var_bind_table = self.cmd_gen.nextCmd(
			cmdgen.CommunityData(self.community_str),
			cmdgen.UdpTransportTarget((address, self.port)),
			oid
		)

		# Check for errors
		if err_indication or err_status:
			self.walk_error(err_indication, err_status,
							err_index, address, var_bind_table)
		else:
			return var_bind_table


	def get_info(self, host):
		"""docstring"""

		self.db_print('Getting info for ', host.ip)
		print('\nGetting info for ' + str(host.ip))

		host.name = self.get_hostname(host)

		host.interface = self.get_interface(host)

		host.mac = self.get_mac(host)

		host.neighbors = self.get_neighbors2(host)
		
		self.get_type(host)
		
		host.if_descr = self.get_if_descr(host)
		host.ent_table_nr = self.get_ent_table_nr(host)
		host.vlan_id = self.get_vlan_id(host)
		self.get_port_list(host)

		self.network[host.id] = { 'mac': host.mac, 'name': host.name,
								  'ip': host.ip, 'interface': host.interface,
								  'neighbors': host.neighbors }


	def get_port_list(self, host):
		"""Find where end devices are connected on the network"""

		port_list = {}
		results = self.walk2(host.ip, '1.3.6.1.2.1.17.4.3.1.2', host.vlan_id)

		if results is None:
			return None

		for result in results:
			for name, val in result:	
				host.port_list[self.dec_to_mac(str(name)[23:])] = int(val)

		from pprint import pprint
		pprint(vars(host))


	def dec_to_mac(self, dec_string):
		"""Convert decimal MAC address to hex"""

		hex_string = ''
		numbers = dec_string.split('.')

		for number in numbers:
			hex_string += str(hex(int(number))[2:].zfill(2))

		return hex_string


	def get_hostname(self, host):
		"""docstring"""

		self.db_print('getHostName')
		print('Getting hostname')
		hostname = ''

		var_binds = self.get(host.ip, self.oid.hostname)

		if var_binds is None:
			return ''

		for name, val in var_binds:
			hostname = str(val)
			self.db_print(val.prettyPrint())

		return hostname


	def get_interface(self, host):
		"""docstring"""

		self.db_print('interface for host ', host.name)
		print('Getting interface')

		ip_found = False
		interface = ''

		result = self.walk(host.ip, self.oid.interface)

		if result is None:	# catch error
			return 0

		for var_bind_table_row in result:
			for name, val in var_bind_table_row:

				ip_found = self.search_string_for_ip(name, host)
				if ip_found:
					self.db_print('interface of host is: ', str(val))
					interface = int(val)
				self.db_print(name.prettyPrint())

		return interface


	def get_if_descr(self, host):
		"""Get the description of the interface"""

		if_descr = ''

		result = self.get(host.ip, '1.3.6.1.2.1.2.2.1.2.' + str(host.interface))

		if result is None:
			return ''

		for name, val in result:
			if_descr = str(val)

		return if_descr


	def get_ent_table_nr(self, host):
		"""Get the correct place of vlan id in entLogicalDescr table"""

		ent_table_nr = 0

		results = self.walk(host.ip, '1.3.6.1.2.1.47.1.2.1.1.2')

		if results is None:
			return 0

		for result in results:
			for name, val in result:
				if str(val) == host.if_descr.lower():
					ent_table_nr = str(name)[-1]

		return ent_table_nr


	def get_vlan_id(self, host):
		"""Get the vlan id from entLogicalDescr table"""

		vlan_id = ''

		result = self.get(host.ip, '1.3.6.1.2.1.47.1.2.1.1.4.' + str(host.ent_table_nr))

		if result is None:
			return ''

		for name, val in result:
			vlan_id = str(val)

		return vlan_id


	def search_string_for_ip(self, name, host):
		"""Search for the host's ip in the snmp response"""

		ip_found = ''
		if(str(name).find(self.oid.interface + '.') != -1):
			ip_found = str(name)[21:]
			if ip_found == host.ip:
				return True

		return False


	def get_mac(self, host):
		"""Get host's MAC address"""

		self.db_print('get mac for ' + host.ip)
		print('Getting MAC address')
		mac = ''

		result = self.get(host.ip, self.oid.mac + '.' + str(host.interface))

		if result is None:	# catch error
			return ''

		for name, val in result:
			mac = host.hex_to_mac(val)
			self.db_print('mac address: ', val.prettyPrint())

		return mac


	def get_type(self, host):
		"""docstring"""

		type_found = False
		
#		typeFound = self.routerCheck(host)
		if self.router_check(host) == False:
			print(str(host.ip) + ' is not a router')
			if self.switch_check(host) == False:
				print(str(host.ip) + ' is not a switch')
				#add printer check
				host.type = 'computer'


	def router_check(self, host):
		"""docstring"""

		self.db_print('checking if ' + str(host.ip) + ' is a router')
		print('Checking if ' + str(host.ip) + ' is a router')

		result = self.get(host.ip, self.oid.type)

		if result != None:
			for name, val in result:
				#print(val.prettyPrint())
				if int(val) == 1:
					print(str(host.ip) + ' is a router')
					host.type = 'router'
					return True
				else:
					return False

		else:
			return False


	def switch_check(self, host):
		"""docstring"""

		print('Checking if ' + str(host.ip) + ' is a switch')
		number_of_ports = None
		cost_to_root = None
		lowest_cost_port = None

		#print(oid.numOfPorts)

		result = self.get(host.ip, self.oid.num_of_ports)

		if result != None:
			for name, val in result:
				number_of_ports = int(val)
				print('number of ports: ' + str(number_of_ports))

		else: return False

		result = self.get(host.ip, self.oid.cost_to_root)

		if result != None:
			for name, val in result:
				cost_to_root = int(val)
				print('cost to root: ' + str(cost_to_root))

		else: return False

		result = self.get(host.ip, self.oid.lowest_cost_port)

		if result != None:
			for name, val in result:
				lowest_cost_port = int(val)
				print('lowestCostPort: ' + str(lowest_cost_port))

		else: return False

		if number_of_ports != None and cost_to_root != None and lowest_cost_port != None:
			host.type = 'switch'
			return True

		else: return False


	def get_host_id(self, host_ip):
		"""docstring"""

		for host in self.host_list:
			if host_ip == host.ip:
				return host.id
		return None


	def get_neighbors2(self, host):	#needs more testing
		"""docstring"""

		print('Getting neighbors')
		neighbors = []
		host.visited = True

		results = self.walk(host.ip, self.oid.neighbors2)

		if results is None:
			return []

		for result in results:
			for name, val in result:
				new_host = Host()
				new_host.ip = new_host.hex_to_ip(val)
				new_host.id = self.get_host_id((new_host.ip))
				if new_host.id is not None:
					neighbors.append(new_host.id)

		return neighbors


	def get_neighbors(self, host):
		"""docstring"""

		self.db_print('getNeighbors for ' + str(host.ip))
		neighbors = []
		host.visited = True
		exists = False

		var_bind_table = self.walk(host.ip, self.oid.neighbors)

		if var_bind_table is None:	# catch error
			return []

		for var_bind_table_row in var_bind_table:
			for name, val in var_bind_table_row:
				if(str(name).find(self.oid.neighbors) != -1):
					self.db_print('FOUND IP ADDRESS')
					if(len(val) != 0):
						new_host = Host()
						if(val.__class__.__name__ == 'OctetString'):
							new_host.ip = new_host.hex_to_ip(val)
							new_host.id = self.get_host_id(new_host.ip)
							new_host.mac = self.get_mac_of_ip(host, new_host)
							self.db_print('adding ' + new_host.ip)
							if(new_host.id != None):
								neighbors.append(new_host.id)
							else:
								self.db_print('A host in neighbor list is None')
#						for host in self.hosts:
#						for someHost in self.hostList:
#							if someHost.ip == newHost.ip:
#								exists = True

#						if not exists:
#							self.hosts.append(newHost)
#							self.hostList.append(newHost)
				#print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))

		self.db_print('NEIGHBORS FOUND:')
#		for counter, host in enumerate(self.hosts):
		for counter, host in enumerate(self.host_list):
			if(counter == 0):
				self.db_print(host.ip)
				continue
			#if(host.ip.__class__.__name__ == 'OctetString'):
				#host.ip = host.hexToOct(host.ip)
			#print str(host.ip)

		#return numOfNeighbors

		return neighbors


	def get_mac_of_ip(self, host, new_host):
		"""docstring"""

		self.db_print('getting mac for ' + str(new_host.ip) + ' from ' + str(host.ip))
		self.db_print('interface: ' + str(host.interface))
								#ipNetToMediaPhysAddress	#interface
		result = self.get(host.ip, '1.3.6.1.2.1.4.22.1.2' + '.' + str(host.interface) + '.' + str(new_host.ip))

		if result is None:
			return ''

		for name, val in result:
			self.db_print('converting mac: ' + val.prettyPrint())
			mac = new_host.hex_to_mac(val)

		#print('mac of neighbor ' + str(newHost.ip) + ' is ' + mac)

		return mac


	def print_hosts(self):
		"""docstring"""

		for counter, host in enumerate(self.host_list):
			print('\nHost ' + str(counter) + ': ' + host.name)
			print('visited: ' + str(host.visited))
			print('ip: ' + host.ip)
			print('mac: ' + host.mac)
			print('type: ' + host.type)
			print('interface: ' + str(host.interface))
			print('neighbors: ')
			for neighbor in host.neighbors:
				print('\t' + str(neighbor))


	def print_network(self):
		"""docstring"""

		self.db_print('network dictionary:')
		for key, value in self.network.iteritems():
			print key, value
			for neighbor in self.network[key]['neighbors']:
				print neighbor


	def get_vlans(self, host):
		"""docstring"""

		self.db_print('getVLANs')
		replies = []

		var_bind_table = self.walk(host.ip, self.oid.vlans)

		for var_bind_table_row in var_bind_table:
			for name, val in var_bind_table_row:
				#print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
				
				if int(val) == 1:
					replies.append(name)
					#print('vlan ' + str(name) + ' is operational')

		for reply in replies:
			vlan = VLAN()
			vlan.number = int(str(reply).split('.')[-1])
	
			if vlan.number not in self.subnets:
				self.subnets[str(vlan.number)] = { 'hosts': [] }
#			print(vlan.number)
			#self.vlans.append(vlan)

		print('subnets:')
		print(self.subnets)


	def get_macs_on_vlan(self, vlan):
		"""docstring"""

		self.db_print('getMACsOnVLAN ', str(vlan.number))

		error_indication, error_status, error_index, var_bind_table = self.cmd_gen.nextCmd(
			cmdgen.CommunityData('menandmice@'+str(vlan.number)),
			cmdgen.UdpTransportTarget(('192.168.60.254', 161)),
			'.1.3.6.1.2.1.17.4.3.1.1'
		)

		if error_indication:
			print(error_indication)
		else:
			if error_status:
				print('%s at %s' % (
					error_status.prettyPrint(),
					error_index and var_bind_table[-1][int(error_index)-1] or '?'
					)
				)
			else:
				for var_bind_table_row in var_bind_table:
					for name, val in var_bind_table_row:
						print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
						host = Host(val)
						#host.mac = val
						vlan.hosts.append(host)

		for host in vlan.hosts:
			self.get_ip_for_host(vlan, host)


	def get_ip_for_host(self, vlan, host):
		"""docstring"""

		self.db_print('get_IP_For_Host ', str(host.mac.prettyPrint()))

		error_indication, error_status, error_index, var_bind_table = self.cmd_gen.nextCmd(
			cmdgen.CommunityData('menandmice@'+str(vlan.number)),
			cmdgen.UdpTransportTarget(('192.168.60.254', 161)),
			'1.3.6.1.2.1.4.22.1.2.29'
		)

		if error_indication:
			print(error_indication)
		else:
			if error_status:
				print('%s at %s' % (
					error_status.prettyPrint(),
					error_index and var_bind_table[-1][int(error_index)-1] or '?'
					)
				)
			else:
				for var_bind_table_row in var_bind_table:
					for name, val in var_bind_table_row:
						print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
						reply = str(name)
						if(reply.find('1.3.6.1.2.1.4.22.1.2.29.') != -1):
							ip = reply[24:]
							host.ip = ip
						if (val == host.mac):
							print('mac address ' + str(host.mac.prettyPrint()) + ' has ip: ' + ip)


	def generate_xml(self):
		"""docstring"""

		xml = dicttoxml(self.network)
		with open('network.xml', 'w') as my_file:
			my_file.write(xml)


	def generate_json(self):
		"""docstring"""

		with open('network.json', 'w') as my_file:
			json.dump(self.network, my_file)


	def db_print(self, *args):
		"""docstring"""

		if(self.debug_mode):
			output = ''
			for arg in args:
				output += str(arg)
			print('## ' + output)


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

	arguments = [address, community, port, debug_mode]
	return arguments


def kill(why):
	"""Kill the program"""
	print(why)
	sys.exit(1)


def main():
	"""Main function to invoke the NetCrawler"""

	arguments = parse_input(sys.argv)
	crawler = Crawler(arguments)

	#print('Address is ' + str(crawler.address) + ' Port is ' + str(crawler.port))

	# first round to see how switches and routers are connected
	crawler.initialize()
	crawler.crawl()

	crawler.print_hosts()

	crawler.generate_xml()
	crawler.generate_json()

	#draw_net = drawnetwork.DrawNetwork()
	#draw_net.draw(crawler.network)


if __name__ == '__main__':
	main()