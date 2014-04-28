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
		self.interface = 0		# current interface host is listening onll
		self.neighbors = []		# hosts connected to this host
		#self.if_descr = ''
		self.ent_table_nr = 0
		self.vlan_id = ''
		self.port_list = {}

		self.if_table = {}
		self.serial_number = ''
		self.responds = True
