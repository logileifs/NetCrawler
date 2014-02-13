from pysnmp.entity.rfc3413.oneliner import cmdgen

class Crawler:
	"""This is the main class"""

	def __init__(self, *args):
		"""Crawler constructor, takes port and address as arguments"""
		self.port = args[0]
		self.address = args[1]
		self.cmdGen = cmdgen.CommandGenerator()


	def getPort(self):
		return self.port


	def getAddress(self):
		return self.address


	def getHello(self):
		return 'hello'

	
	def getNext(self):
		errorIndication, errorStatus, errorIndex, varBindTable = self.cmdGen.nextCmd(
			cmdgen.CommunityData('menandmice'),
			cmdgen.UdpTransportTarget(('192.168.60.254', 161)),
			'1.3.6.1.2.1.2.2.1',
		)

		if errorIndication:
			print(errorIndication)
		else:
			if errorStatus:
				print('%s at %s' % (
					errorStatus.prettyPrint(),
					errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
					)
				)
			else:
				for varBindTableRow in varBindTable:
					for name, val in varBindTableRow:
						print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
