class Host:
	"""PODO class for host"""

	def __init__(self):
		"""Constructor"""
		self.mac = ''			# MAC address
		self.ip = ''			# IP address
		self.port = 0			# 
		self.type = ''
		self.name = ''			# hostname
		self.visited = False	# has this host been checked or not
		self.interface = 0		# current interface host is listening on
		self.neighbors = []		# hosts connected to this host


	def hexToOct(self, hexNum):
		numbers = str(hexNum.asNumbers())
		octet = numbers.replace('(', '').replace(')', '').replace(' ', '').replace(',', '.')
		return octet

	def hexToString(self, hexNum):
		numbers = str(hexNum.asNumbers())
		numbers = numbers.replace('(', '').replace(')', '').replace(',', '')
		numList = numbers.split(' ')
		
		del numbers
		numbers = ''
		
		for num in numList:
			numbers += str(hex(int(num))[2:].zfill(2))
		
		return numbers
