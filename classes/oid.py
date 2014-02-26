class OID:
	"""OID class"""

	def __init__(self):
		self.hostName = '1.3.6.1.4.1.9.9.23.1.3.4.0'	#1.3.6.1.4.1.9.2.1.3 try this one
		self.neighbors = '1.3.6.1.4.1.9.9.23.1.2.1.1.20'
		self.vlans = '.1.3.6.1.4.1.9.9.46.1.3.1.1.2'
		self.macsOnVlan = '.1.3.6.1.2.1.17.4.3.1.1'
		self.interface = '1.3.6.1.2.1.4.20.1.2'
		self.mac = '1.3.6.1.2.1.2.2.1.6'
		self.type = '1.3.6.1.2.1.4.1.0'	# 1 = router, 2 = not router
		#self.sysDescr = '1.3.6.1.2.1.1.1.0'