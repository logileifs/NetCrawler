"""This script prompts a user to enter a message to encode or decode
using a classic Caeser shift substitution (3 letter shift)"""

from pysnmp.entity.rfc3413.oneliner import cmdgen
from pingsweep import PingSweep
from vlan import VLAN
from host import Host
from oid import OID
from dicttoxml import dicttoxml
import ipcalc
#import socket
import json
#import sys

class Crawler:
	"""This is the main class"""
	#oid = None

	def __init__(self, *args):
		"""Crawler constructor, takes port and address as arguments"""
		oid = OID()
		self.port = args[0]
		self.address = args[1]					# starting point
		self.range = []

		net = ipcalc.Network(self.address)
		print('Size of network: ' + str(net.size()))
		#print('broadcast address: ' + str(net.broadcast()))

		pingsweep = PingSweep(net)
		self.range = pingsweep.sweep()
		self.host_list = []

		#print('crawler address range:')
		for counter, ip in enumerate(self.range):
			host = Host()
			host.ip = ip
			host.id += str(counter)
			self.host_list.append(host)
			#print(counter)

		print('Alive hosts:')
		for host in self.host_list:
			print(host.ip)

		self.community_str = args[2]
		self.debug_mode = args[3]
		self.cmd_gen = cmdgen.CommandGenerator()
		self.hosts = []
		self.vlans = []
		self.oid = OID()

		self.network = {}
		self.subnets = {}

		host = Host()
		host.ip = self.address
		self.hosts.append(host)


	def get_error(self, indication, status, index, address):
		"""docstring"""
		
		print('SNMPGET ERROR')

		# Check for errors and print out results
		if indication:
			print(str(indication) + ' from ' + str(address))
		elif status:
			print(status)


	def walk_error(self, indication, status, index, address, var_bind_table):
		"""docstring"""

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


	def walk(self, address, oid):
		"""docstring"""

		error_indication, error_status, error_index, var_bind_table = self.cmd_gen.nextCmd(
			cmdgen.CommunityData(self.community_str),
			cmdgen.UdpTransportTarget((address, self.port)),
			oid
		)

		# Check for errors
		if error_indication or error_status:
			self.walk_error(error_indication, error_status, error_index, address, var_bind_table)
		else:
			return var_bind_table


	def get_info(self, host):
		"""docstring"""

		self.db_print('Getting info for ', host.ip)
		print('\nGetting info for ' + str(host.ip))

		host.name = self.get_hostname(host)

		host.interface = self.get_interface(host)

		host.mac = self.get_mac(host)

#		host.neighbors = self.getNeighbors(host)
		host.neighbors = self.get_neighbors2(host)

		self.get_type(host)

		#self.getVLANs(host)

		self.network[host.id] = { 'mac': host.mac, 'name': host.name, 'ip': host.ip, 'interface': host.interface, 'neighbors': host.neighbors }

		self.db_print('network dictionary:')
		
		"""for key, value in self.network.iteritems():
			print key, value
			if key == 'neighbors':
				print('key = neighbors')
			for neighbor in self.network[key]['neighbors']:
				print neighbor"""


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


	def search_string_for_ip(self, name, host):
		"""Search for the host's ip in the snmp response"""

		ip_found = ''
		if(str(name).find(self.oid.interface + '.') != -1):
			ip_found = str(name)[21:]
			if ip_found == host.ip:
				return True

		return False


	def get_mac(self, host):
		"""docstring"""

		self.db_print('get mac for ' + host.ip)
		print('Getting MAC address')
		mac = ''

		result = self.get(host.ip, self.oid.mac + '.' + str(host.interface))

		if result is None:	# catch error
			return ''

		for name, val in result:
			mac = host.hex_to_string(val)
			self.db_print('mac address: ', val.prettyPrint())

			#print(str(val))
			#host.mac = host.hexToString(val)
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
				#print(name.prettyPrint())
				#print(val.prettyPrint())
				new_host = Host()
				new_host.ip = new_host.hex_to_oct(val)
				#print('newHost.ip = ' + str(newHost.ip))
				new_host.id = self.get_host_id((new_host.ip))
				#print('newHost.id = ' + str(newHost.id))
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
							new_host.ip = new_host.hex_to_oct(val)
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
			mac = new_host.hex_to_string(val)

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


	