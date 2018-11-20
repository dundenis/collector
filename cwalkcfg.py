import ConfigParser
import sys
import os

class cwalk_parser(ConfigParser.ConfigParser):

    def __init__(self,file):
        ConfigParser.ConfigParser.__init__(self)
        self.read(file)
        self.path = sys.path[0]

    def commands(self):
        file = self.get('common','commands')
        lines = open(os.path.join(self.path,file))
        commands = [l.strip() for l in lines if not (l.startswith('#') or l.strip()=='')]
        return commands

    def devices(self):
        devices = []
        dev = {'host':'','ip':'','login':'','password':''}
        file = self.get('common','devices')
        lines = open(os.path.join(self.path,file))

        for line in lines:
            #ignore comment and blank lines
            if line.startswith('#') or line.strip() == '':
                continue
            #get device items
            dev['host'],dev['ip'],dev['login'],dev['password'] =[l.strip() for l in line.strip().split(',') ]
            # Add to device
            devices.append(dev.copy())
        return devices

    def output(self):
        dir = os.path.join(self.path,self.get('common','output')) 
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir
