class Crawler:
	"""This is the main class"""

	def __init__(self, *args):
		"""Crawler constructor, takes port and address as arguments"""
		self.port = args[0]
		self.address = args[1]

#	def __init__(self, address):
#		self.address = address

	def getPort(self):
		return self.port

	def getAddress(self):
		return self.address

	def getHello(self):
		return 'hello'

	def getHelloWorld(self):
		return 'hello world'