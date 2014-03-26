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
		self.if_descr = ''
		self.ent_table_nr = 0
		self.vlan_id = ''
		self.port_list = {}


	def hex_to_ip(self, hexNum):
		numbers = str(hexNum.asNumbers())
		octet = numbers.replace('(', '').replace(')', '').replace(' ', '').replace(',', '.')
		return octet

	def hex_to_mac(self, hexNum):
		numbers = str(hexNum.asNumbers())
		numbers = numbers.replace('(', '').replace(')', '').replace(',', '')
		numList = numbers.split(' ')
		
		del numbers
		numbers = ''
		
		for num in numList:
			numbers += str(hex(int(num))[2:].zfill(2))
		
		return numbers
