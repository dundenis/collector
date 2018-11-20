#!/usr/bin/env python

import re

class _RegExLibFlap:
    _reg_time = re.compile(r'Time\s*:\s*S:([\d\-]*)\s([\d\:]*)\s*E:([\d\-]*)\s([\d\:]*)')
    _reg_bd = re.compile(r'VLAN/BD\s*:\s*-/(\d*)')
    _reg_mac = re.compile(r'MAC Address\s*:\s*(\w{4}-\w{4}-\w{4})')
    _reg_movenm = re.compile(r'MoveNum\s*:\s*(\d*)')
    
    __slots__ = ['time', 'bd', 'mac', 'movenm']
    
    def __init__(self, line):
        self.time = self._reg_time.match(line)
        self.bd = self._reg_bd.match(line)
        self.mac = self._reg_mac.match(line)
        self.movenm = self._reg_movenm.match(line)


class _ParseFlap:
    def __init__(self, output):
        self.iter = iter(output.split('\n'))
        self.list = []
    def do(self):
        for line in self.iter:
            match_reg = _RegExLibFlap(line)
            if match_reg.time:
                time_cp = match_reg.time.groups() 
                time_desc = ['Start Date','Start Time','End Date', 'End Time']
            if match_reg.bd:
                bd = match_reg.bd.group(1)
            if match_reg.mac:
                mac = match_reg.mac.group(1)
            if match_reg.movenm:
                move_nm = match_reg.movenm.group(1)
                move_nm = int(move_nm)
                iter_dict = {time_desc[i]: time_cp[i] for i in range(4)}
                iter_dict.update({'Bridge Domain': bd, 'MAC Address': mac, 'Move number': move_nm})
                self.list.append(iter_dict)



