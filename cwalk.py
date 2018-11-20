#!/usr/bin/env python

import re
import os
import sys
import time
import multiprocessing as mp
from functools import partial
#from threadpool import *
from cwalkcfg import cwalk_parser
# sys.path.append(r'./')
from cwalklib import *

#threads = 10
conf=cwalk_parser(os.path.join(sys.path[0],'cwalk.conf'))

print '='*100
print 'Number of commands:\t%s'%len(conf.commands())
print 'Number of devices:\t%s'%len(conf.devices())
print 'Output directory:\t%s'%conf.output()
print '='*100


class _Report:
	def __init__(self):
		self.template = ""

	def make(self, tmp, cdict):
		self.template = tmp
		global data_dir
		res = ""
		try:
			with open(os.path.join(data_dir,'default_report.csv'),'w') as report:
				for key in cdict.keys():
					for item in range(len(cdict[key])):
						res += "%s;"%key
						res += self.template%cdict[key][item]
						res += "\n"
				report.write(res)
			print "Report is generated."
		except IOError as io:
			print "Can't write report -- io error:" + "\n" + io





#print "%s-%s: connection timout" % (str(datetime.now()),device['host'])
clog = None

# Device List
dev_lst = conf.devices()

# Command List
#cmdlst=conf.commands()

# Output directory
data_dir = conf.output()


def collect_pool(num_processes=4):
	manager = mp.Manager()
	collected_dict = manager.dict()
	_lock = manager.Lock()
	pool = mp.Pool(num_processes)
	pool.map(partial(CollectData, manager_dict = collected_dict, lock = _lock), dev_lst)
	pool.close()
	pool.join()
	return collected_dict


if __name__ == '__main__':
	
	results_dict = collect_pool()
	template_report = "%(Bridge Domain)s;%(MAC Address)s;%(Move number)s"
	report = _Report()
	report.make(template_report, results_dict)






