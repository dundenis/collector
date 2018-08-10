#!/usr/bin/env python

import re
import os
import sys
import time
import paramiko
import netmiko
from datetime import datetime

def match_lst(text, regex):
    text = '\n'.join(text.splitlines())
    re_obj = re.compile(regex, re.MULTILINE)
    return re_obj.findall(text)

def diagnose_mode(ssh_connection):
    result = ""
    if re.search("\-diagnose", ssh_connection.base_prompt):
	pass
    else:
	ssh_connection.config_mode()
	ssh_connection.base_prompt += "-diagnose"
	result = ssh_connection.send_command("diagnose",expect_string=ssh_connection.base_prompt)
    return result


def exit_diagnose_mode(ssh_connection):
    result = ""
    if re.search("\-diagnose", ssh_connection.base_prompt):
	ssh_connection.base_prompt = ssh_connection.base_prompt.replace('-diagnose', '')
	result = ssh_connection.send_command("quit",expect_string=ssh_connection.base_prompt)
	ssh_connection.exit_config_mode()
    else:
	pass
    return result


def exec_command(ssh_connection,command):
    print ssh_connection.base_prompt
    print "Executing: \"" + command + "\""
    if (command == "diagnose"):
	result = diagnose_mode(ssh_connection)
    elif (command == "quit"):
	result = exit_diagnose_mode(ssh_connection)
    else:
	if re.search("display diagnostic\-information", command) or re.search("display diag", command):
	    result = ssh_connection.send_command_expect(command, delay_factor=5)
	else:
	    result = ssh_connection.send_command_expect(command)
    return result


def connect(d,cmdlst,data_dir,LOG):
	try:
		collect_time = datetime.now()
		print str(collect_time) + " - Checking " + d['host'] + "..."
		LOG.write(str(collect_time) + " - Checking " + d['host'] + "...\n")
		# establish a connection to the device
		ssh_connection = netmiko.ConnectHandler(
			device_type='huawei',
			ip=d['ip'],
			username=d['login'],
			password=d['password'])
	except netmiko.ssh_exception.NetMikoTimeoutException:
		print "\n%s: Connection timout" % d['host']
		LOG.write("\n%s - %s: Connection timout" % (str(datetime.now()),d['host']))
	except netmiko.ssh_exception.NetMikoAuthenticationException:
		print "\n%s: Authentication problem" % d['host']
		LOG.write("\n%s - %s: Authentication problem" % (str(datetime.now()),d['host']))
	else:
		# prepend the command prompt to the result (used to identify the local host)
		
		hostname = d['host']
		result = ssh_connection.find_prompt() + "\n"
		#open logfile to write parsed results
		with open(os.path.join(data_dir,"collect_errors.log"), "a") as ce_log:
			for c in cmdlst:
				print c
				regex_err = r'(\d*/\d*)\s*([\d-]*)\s*([\d-]*)'
				re_m_lst = match_lst(exec_command(ssh_connection,c),regex_err)
				for l in re_m_lst:
					sev ='OK'
					if l[1] == '--' or l[2] == '--':
						sev = 'N/A'
					elif int(l[1])!=0 or int(l[2])!=0: 
						sev = 'CRITICAL'
					ce_log.write(str(collect_time) + ";" + hostname + ";" + l[0] + ";" + l[1] + ";" + l[2]+";" + sev + "\n")
		ssh_connection.disconnect()
		ce_log.close()

#	FO=open(os.path.join(data_dir,log.log),'w+')
#
#	for c in cmdlst:
#		print c
#		FO.write("""
#
#===============================================================================
#                 """ + c + """
#===============================================================================
#""")
#	    FO.write(exec_command(ssh_connection,c) + "\n")
#
#	# close SSH connection
#	ssh_connection.disconnect()
#	FO.close()
