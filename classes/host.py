class Host:
	"""PODO class for host"""

	def __init__(self):
		"""Constructor"""
		self.mac = ''
		self.ip = ''
		self.port = 0
		self.name = ''
		self.visited = False
		self.interface = 0


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
			numbers = numbers + str(hex(int(num))[2:].zfill(2))
		
		return numbers
