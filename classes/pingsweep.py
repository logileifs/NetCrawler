"""PingSweep module"""

from time import sleep
import multiprocessing
from tqdm import tqdm
import subprocess
import ipcalc
import sys
import os

class PingSweep:
	"""docstring for PingSweep"""
	#def __init__(self, net):
		#self.net = net
		#self.size = net.size()
	

	def pinger(self, job_q, results_q):
		"""the pinger job for each thread"""

		devnull = open(os.devnull, 'w')
		while True:
			ip = job_q.get()
			if ip is None: break

			try:
				#only works on linux/unix
				subprocess.check_call(['ping', '-c1', '-w2', ip], stdout=devnull)
				results_q.put(ip)
			except:
				pass

	def sweep(self, net):
		"""initialize threads and give each a pinger job"""

		addresses = []
		pool_size = net.size()
		#print('pool size: ' + str(pool_size))

		jobs = multiprocessing.Queue()
		results = multiprocessing.Queue()

		pool = [ multiprocessing.Process(target=self.pinger, args=(jobs, results))
				 for i in range(pool_size) ]

		for p in pool:
			p.start()

		for ip in tqdm(net):
			sleep(0.020)
			jobs.put(str(ip))
			#print(ip)

		for p in pool:
			jobs.put(None)

		for p in tqdm(pool):
			p.join()

		while not results.empty():
			ip = results.get()
			addresses.append(ip)

		return addresses


def main():
	"""main function"""

	net = ipcalc.Network(sys.argv[1])
	print('broadcast address: ' + str(net.broadcast()))	
	pingsweep = PingSweep()
	address_range = []
	address_range = pingsweep.sweep(net)

	for address in address_range:
		print(address)


if __name__ == '__main__':
	main()