#!/usr/bin/env python

import re
import os
import sys
import time

from threadpool import *
from cwalkcfg import cwalk_parser
# sys.path.append(r'./')
from cwalklib import *

threads = 10
conf=cwalk_parser(os.path.join(sys.path[0],'cwalk.conf'))

print """==============================================================================="""
print 'Number of commands:\t%s'%len(conf.commands())
print 'Number of devices:\t%s'%len(conf.devices())
print 'Output directory:\t%s'%conf.output()
print """==============================================================================="""

# Device List
devlst=conf.devices()

# Command List
cmdlst=conf.commands()

# Output directory
data_dir = conf.output()

print """\n\tList of CLI commands:\n"""
for c in cmdlst:
    print "\t* " + c

print """\n==============================================================================="""

time_stamp=time.strftime("%y%m%d%H%M",time.localtime(time.time()))

# Open log file
LOG=open(os.path.join(data_dir,"cwalk-" + time_stamp + ".log"),'w')

# Generate work threads
requests=[]
main=ThreadPool(threads)
time_stamp=time.strftime("%y%m%d%H%M",time.localtime(time.time()))

# Add tasks to the poll
for d in devlst:
    requests.append(WorkRequest(connect,[d,cmdlst,data_dir,LOG]))

# Start
for req in requests:
    main.putRequest(req)
    time.sleep(1.0)
main.wait()

LOG.close()

