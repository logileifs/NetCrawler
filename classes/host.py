"""docstring"""
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
		self.interface = 0		# current interface host is listening on
		self.neighbors = []		# hosts connected to this host


	def hex_to_oct(self, hex_num):
		"""docstring"""
		
		numbers = str(hex_num.asNumbers())
		octet = numbers.replace('(', '').replace(')', '').replace(' ', '').replace(',', '.')
		return octet

	def hex_to_string(self, hex_num):
		"""docstring"""

		numbers = str(hex_num.asNumbers())
		numbers = numbers.replace('(', '').replace(')', '').replace(',', '')
		num_list = numbers.split(' ')
		
		del numbers
		numbers = ''
		
		for num in num_list:
			numbers += str(hex(int(num))[2:].zfill(2))
		
		return numbers
