class Host:
	"""PODO class for host"""

	def __init__(self):
		"""Constructor"""
		self.mac = ''
		self.ip = ''
		self.port = 0
		self.name = ''
		self.visited = False


	def hexToOct(self, hexNum):
		numbers = str(hexNum.asNumbers())
		octet = numbers.replace('(', '').replace(')', '').replace(' ', '').replace(',', '.')
		return octet