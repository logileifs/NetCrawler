
class Host:
	"""PODO class for host"""

	def __init__(self):
		"""Constructor"""
		self.id = 'host'
		self.mac = ''			# MAC address on this subnet
		self.ip = ''			# IP address on this subnet
		self.port = None		# 
		self.type = ''
		self.name = ''			# hostname
		self.visited = False	# has this host been checked or not
		self.interface = None	# current interface host is listening on
		self.neighbors = []		# hosts connected to this host
		self.if_descr = ''
		self.ent_table_nr = None
		self.vlan_id = ''
		self.port_list = {}

		self.if_table = {}
		self.serial_number = ''
		self.model = ''
		self.responds = True	# is the host answering snmp requests
		self.types = []
		self.interfaces = []
		self.ips = []
		self.macs = []
		self.connections = []
		self.vendor = ''

		self.connections2 = []


	def is_switch(self):
		"""Return true if host is a switch"""

		return 'switch' in self.types


	def is_router(self):
		"""Return true if host is a router"""

		return 'router' in self.types


	def add_type(self, host_type):

		if host_type not in self.types:
			self.types.append(host_type)


	def add_ip(self, ip):
		"""Add a new ip address to this host"""

		if ip not in self.ips:
			self.ips.append(ip)


	def add_mac(self, mac):
		"""Add a new mac address to this host"""

		if mac not in self.macs:
			self.macs.append(mac)


	def add_interface(self, interface):
		"""Add a new interface to this host"""

		if not self.interface_exists(interface):
			self.interfaces.append(interface)


	def interface_exists(self, interface):
		"""Check if this interface already exists at this host"""

		for intf in self.interfaces:
			if intf.number == interface.number:
				return True

		return False


	def get_interface(self, number):
		"""Return interface with number=number, otherwise return None"""

		for intf in self.interfaces:
			if intf.number == number:
				return intf

		return None


	def get_interface_by_port(self, port):

		for intf in self.interfaces:
			if intf.port == port:
				return intf

		return None


	def get_interface_by_mac(self, mac):
		"""Return the interface a mac address has been learned on"""

		for intf in self.interfaces:
			if mac in intf.macs_connected:
				return intf

		return None


	def get_interface_by_descr(self, descr):
		"""Return the interface with descr"""

		for intf in self.interfaces:
			if descr == intf.descr:
				return intf

		return None


	def add_neighbor(self, neighbor):

		if neighbor not in self.neighbors:
			self.neighbors.append(neighbor)


	def add_connection(self, neighbor, port):

		if (neighbor, port) not in self.connections:
			self.connections.append((neighbor, port))


	def print_host(self):

		print('\tid: ' + str(self.id))
		print('\tmac: ' + str(self.mac))
		print('\tip: ' + str(self.ip))
		#print('\tport: ' + str(self.port))
		print('\ttype: ' + str(self.type))
		print('\tname: ' + str(self.name))
		print('\tvisited: ' + str(self.visited))
		#print('\tinterface: ' + str(self.interface))
		print('\tif_descr: ' + str(self.if_descr))
		print('\tvlan_id: ' + str(self.vlan_id))
		print('\tserial number: ' + str(self.serial_number))
		print('\tmodel: ' + str(self.model))
		print('\tresponds: ' + str(self.responds))


	def print_interfaces(self):

		for interface in self.interfaces:
			interface.print_interface()


	#def __str__(self):
