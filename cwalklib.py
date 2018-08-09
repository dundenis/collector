#!/usr/bin/env python

import re
import os
import sys
import time
import paramiko
import netmiko


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
	print "\nTrying " + d['host'] + "..."
	LOG.write("\nTrying " + d['host'] + "...")
	# establish a connection to the device
	ssh_connection = netmiko.ConnectHandler(
    	    device_type='huawei',
    	    ip=d['ip'],
    	    username=d['login'],
    	    password=d['password']
	)
    except netmiko.ssh_exception.NetMikoTimeoutException:
	print "\n%s: Connection timout" % d['host']
	LOG.write("\n%s: Connection timout" % d['host'])
    except netmiko.ssh_exception.NetMikoAuthenticationException:
	print "\n%s: Authentication problem" % d['host']
	LOG.write("\n%s: Authentication problem" % d['host'])
    else:
	# prepend the command prompt to the result (used to identify the local host)
	result = ssh_connection.find_prompt() + "\n"

	FO=open(os.path.join(data_dir,d['host']),'w')

	for c in cmdlst:
#	    print c
	    FO.write("""

===============================================================================
                 """ + c + """
===============================================================================
""")
	    FO.write(exec_command(ssh_connection,c) + "\n")

	# close SSH connection
	ssh_connection.disconnect()
	FO.close()
