
class Host:
	"""PODO class for host"""

	def __init__(self):
		"""Constructor"""
		self.id = 'host'
		self.mac = ''			# MAC address
		self.ip = ''			# IP address
		self.port = None			# 
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


	def is_switch(self):
		"""Return true if host is a switch"""

		return 'switch' in self.types


	def is_router(self):
		"""Return true if host is a router"""

		return 'router' in self.types


	def add_interface(self, interface):

		if not self.interface_exists(interface):
			self.interfaces.append(interface)


	def interface_exists(self, interface):

		for intf in self.interfaces:
			if intf.number == interface.number:
				return True

		return False

	def get_interface(self, number):

		for intf in self.interfaces:
			if intf.number == number:
				return intf

		return None


	def get_interface_by_port(self, port):

		for intf in self.interfaces:
			if intf.port == port:
				return intf

		return None


	def print_host(self):

		print('id: ' + str(self.id))
		print('mac: ' + str(self.mac))
		print('ip: ' + str(self.ip))
		print('port: ' + str(self.port))
		print('type: ' + str(self.type))
		print('name: ' + str(self.name))
		print('visited: ' + str(self.visited))
		print('interface: ' + str(self.interface))
		print('if_descr: ' + str(self.if_descr))
		print('vlan_id: ' + str(self.vlan_id))
		print('serial number: ' + str(self.serial_number))
		print('model: ' + str(self.model))
		print('responds: ' + str(self.responds))


	#def __str__(self):
