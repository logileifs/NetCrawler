from pysnmp.entity.rfc3413.oneliner import cmdgen
from vlan import VLAN
from host import Host

class Crawler:
	"""This is the main class"""

	def __init__(self, *args):
		"""Crawler constructor, takes port and address as arguments"""
		self.port = args[0]
		self.address = args[1]
		self.cmdGen = cmdgen.CommandGenerator()
		self.vlans = []

		self.connectedPorts = []
		self.connectedMacs = []
		self.connectedIPs = []

	def getPort(self):
		return self.port


	def getAddress(self):
		return self.address


	def getHello(self):
		return 'hello'


	def getVLANs(self):
		print('getVLANs')
		replies = []
		errorIndication, errorStatus, errorIndex, varBindTable = self.cmdGen.nextCmd(
			cmdgen.CommunityData('menandmice'),
			cmdgen.UdpTransportTarget(('192.168.60.254', 161)),
			'.1.3.6.1.4.1.9.9.46.1.3.1.1.2'
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
						#print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
						replies.append(name)

		for reply in replies:
			vlan = VLAN()
			vlan.number = int(str(reply).split('.')[-1])
			self.vlans.append(vlan)

#		print('vlans:')
#		for vlan in self.vlans:
#			print(vlan.number)
		
#		self.getMACsOnVLAN(self.vlans[1])


	def getMACsOnVLAN(self, vlan):
		print('getMACsOnVLAN ' + str(vlan.number))

		errorIndication, errorStatus, errorIndex, varBindTable = self.cmdGen.nextCmd(
			cmdgen.CommunityData('menandmice@'+str(vlan.number)),
			cmdgen.UdpTransportTarget(('192.168.60.254', 161)),
			'.1.3.6.1.2.1.17.4.3.1.1'
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
						host = Host(val)
						#host.mac = val
						vlan.hosts.append(host)

		for host in vlan.hosts:
			#print(host.mac.prettyPrint())
			self.getIPForHost(vlan, host)
#			print(mac.prettyPrint())
#			print(vlan.convertMacToOct(mac))


	def getIPForHost(self, vlan, host):
		print('getIPForHost ' + str(host.mac.prettyPrint()))

		errorIndication, errorStatus, errorIndex, varBindTable = self.cmdGen.nextCmd(
			cmdgen.CommunityData('menandmice@'+str(vlan.number)),
			cmdgen.UdpTransportTarget(('192.168.60.254', 161)),
			'1.3.6.1.2.1.4.22.1.2.29'
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
						reply = str(name)
						if(reply.find('1.3.6.1.2.1.4.22.1.2.29.') != -1):
							ip = reply[24:]
							host.ip = ip
#							print(ip[24:])
						if (val == host.mac):
							print('mac address ' + str(host.mac.prettyPrint()) + ' has ip: ' + ip)