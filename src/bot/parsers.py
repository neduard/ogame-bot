'''
Created on Jul 30, 2011

@author: eduard
'''

import re

def parse_report(report):
    s = re.search('Resources at .* \[(.*)\] \(.*\) on (.*)', report[0])
    coord = s.group(1)
    date  = s.group(2)
    s = re.search("Metal:[\t ]*([0-9]+\.*[0-9]+)[\t ]*Crystal:[\t ]*([0-9]+\.*[0-9]+)", report[1])
    metal = s.group(1)
    crystal = s.group(2)
    s = re.search("Deuterium:[\t ]*([0-9]+\.*[0-9]+).*", report[2])
    deuterium = s.group(1)
    return (coord, "2011-"+date, metal.replace('.', ''), crystal.replace('.', ''), deuterium.replace('.', ''))

def parse_battle(report):
    s = re.match('Combat at .* \[(.*)\] \((.*)\)', report[0]);
    coord, date = s.group(1), s.group(2)
    s = re.match('([0-9]*.*[0-9]*) Metal, ([0-9]*.*[0-9]*) Crystal and ([0-9]*.*[0-9]*) Deuterium.', report[1])
    metal, crystal, deuterium = s.group(1), s.group(2), s.group(3)
    return (coord, date, metal.replace('.', ''), crystal.replace('.', ''), deuterium.replace('.', ''))