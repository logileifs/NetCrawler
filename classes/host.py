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


	def is_switch(self):
		"""Return true if host is a switch"""

		return 'switch' in self.types


	def is_router(self):
		"""Return true if host is a router"""

		return 'router' in self.types