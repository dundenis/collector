#!/usr/bin/env python

import re
import os
import sys
import time
import paramiko
import netmiko
from datetime import datetime
from cparse import _RegExLibFlap,_ParseFlap

class OperationLog:
	def __init__(self):
		self.MSG = ""

	def WriteToFile(self, MSG):
		tmpmsg = ""
		dataTime = str(datetime.now())
		with open(os.path.join('operation_log.log'),'a') as logfile:
			tmpmsg += dataTime + "--" + MSG 
			print tmpmsg
			logfile.write(tmpmsg + "\n")
			logfile.close()
	
	def _stdout(self, MSG):
		tmpmsg = ""
		dataTime = str(datetime.now())
		#lock.acquire()
		print dataTime + self.MSG
		#lock.release()

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


def exec_command(ssh_connection,command,device):

    #print ssh_connection.base_prompt
    #print "%s--%s: executing command:%s" % (str(datetime.now()),device['host'],command)
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


def CollectData(device,manager_dict, lock):
	cmd = "display mac-address flapping aged-table "
	tmp_dict={}
	hostname = device['host']
	log = OperationLog()
	try:
		lock.acquire()
		log.WriteToFile(hostname + ": start checking")
		lock.release()
		#connect to device via ssh
		ssh_connection = netmiko.ConnectHandler(
			device_type='huawei',
			ip=device['ip'],
			username=device['login'],
			password=device['password'])
	except netmiko.ssh_exception.NetMikoTimeoutException:
		lock.acquire()
		log.WriteToFile(hostname + ": ssh timeout")
		lock.release()
	except netmiko.ssh_exception.NetMikoAuthenticationException:
		lock.acquire()
		log.WriteToFile(hostname + ": authentication failed")
		lock.release()
	else:
		lock.acquire()
		log.WriteToFile(hostname + ": ssh session established successfully")
		lock.release()

		result = ssh_connection.find_prompt() + "\n"
		#for cmd in cmdList:
		lock.acquire()
		log.WriteToFile(hostname + ": send command --> " + cmd)
		lock.release()
		ssh_output = exec_command(ssh_connection,cmd,device)
		parse = _ParseFlap(ssh_output)
		try:
			parse.do()
		except:
			pass
		if parse.list: 
			tmp_dict.update({device['ip']: parse.list})
			manager_dict.update(tmp_dict)
		ssh_connection.disconnect()
		lock.acquire()
		log.WriteToFile(hostname + ": ssh session closed")
		lock.release()

"""
def CollectData(device, manager_dict, lock):
	c = {'10.35.81.21': [{'End Date': u'2018-11-13', 'MAC Address': u'b40c-25e0-4010', 'Bridge Domain': u'1042130', 'Start Time': u'12:14:39', 'End Time': u'12:14:39', 'Move number': 2, 'Start Date': u'2018-11-13'}, {'End Date': u'2018-11-15', 'MAC Address': u'0000-5e00-0133', 'Bridge Domain': u'1040003', 'Start Time': u'19:23:31', 'End Time': u'19:23:31', 'Move number': 1, 'Start Date': u'2018-11-15'}], '10.35.81.22': [{'End Date': u'2018-11-15', 'MAC Address': u'0000-5e00-01aa', 'Bridge Domain': u'1040003', 'Start Time': u'19:23:31', 'End Time': u'19:23:31', 'Move number': 1, 'Start Date': u'2018-11-15'}]}
	
	hostname = device['host']
	log = OperationLog()
	lock.acquire()
	log.WriteToFile(hostname + "--" +"start checking")
	lock.release()
	manager_dict.update(c)
"""