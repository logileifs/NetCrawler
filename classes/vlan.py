class VLAN:
	"""PODO class for VLAN"""

	def __init__(self):
		"""Constructor"""
		self.number = 0
		self.macs = []
		self.ips = []
		self.hosts = []


	def convertMacToOct(self, mac):
		numbers = str(mac.asNumbers())
		octet = numbers.replace('(', '').replace(')', '').replace(' ', '').replace(',', '.')
		return octet