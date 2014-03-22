"""VLAN data class"""

class VLAN:
	"""PODO class for VLAN"""

	def __init__(self):
		"""Constructor"""
		self.number = 0
		self.macs = []
		self.ips = []
		self.hosts = []