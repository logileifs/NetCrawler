from time import sleep
import multiprocessing
import subprocess
import ipcalc
import os

class PingSweep:
	"""docstring for PingSweep"""
	def __init__(self, net):
		self.net = net
		self.size = net.size()
	

	def pinger(self, job_q, results_q):
		DEVNULL = open(os.devnull,'w')
		while True:
			ip = job_q.get()
			if ip is None: break

			try:
				subprocess.check_call(['ping','-c1',ip], stdout=DEVNULL)
				results_q.put(ip)
				sleep(0.05)
			except:
				pass

	def sweep(self):
		addresses = []
		pool_size = self.size
		print('pool size: ' + str(pool_size))

		jobs = multiprocessing.Queue()
		results = multiprocessing.Queue()

		pool = [ multiprocessing.Process(target=self.pinger, args=(jobs,results))
				 for i in range(pool_size) ]

		for p in pool:
			p.start()

#		for i in range(1,255):
		for i in self.net:
#			jobs.put('192.168.60.{0}'.format(i))
			jobs.put(str(i))

		for p in pool:
			jobs.put(None)

		for p in pool:
			p.join()

		while not results.empty():
			ip = results.get()
			addresses.append(ip)
			#print(ip)

		return addresses