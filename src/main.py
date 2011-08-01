#! /usr/bin/python
'''
Created on Jul 29, 2011

@author: eduard
'''

import re, bot.logic, bot.parsers

def mainLoop(bot):
    while True:
        command = raw_input(">");
        if re.match('Resources at .*', command):
            report = [command, raw_input(), raw_input()]
            print "Processing espionaje report..."
            ogbot.addReport(bot.parsers.parse_report(report))
        
        elif re.match('Combat at .*', command):
            report = [command, raw_input()]
            print "Processing combat report..."
            ogbot.addCombatReport(bot.parsers.parse_battle(report))
            
        elif re.match('cprod', command):
            coord = re.match('cprod (-c ?)?(.*)', command)
            if (coord): coord = coord.group(2)
            ogbot.calculate_production(coord, re.search('-c', command) != None)
            
        elif re.match('rent', command):
            print 'Coordonates\tWeighted score\tPlain Score\tNr of cargos'
            for coord, wr, pr, ships in sorted(ogbot.getRentability(), key=lambda y: y[1], reverse = True):
                print str(coord).ljust(15), str(wr).ljust(15), str(pr).ljust(15), str(ships)
            
        elif re.match('gres', command):
            print 'current resources for all planets'
            for id in ogbot.db.get_planet_list():
                x = ogbot.db.get_current_resources(id)
                if (x): print "%s %d %d %d" % (ogbot.db.get_planet_coord(id) + x)
            
        elif re.match('(quit|q)\Z', command):
            print "Exiting..."
            break
        
        else:
            print "Command not found. Only two command so far are cprod [-c] [coord_mask] and rent"    

if __name__ == '__main__':
    print 'Welcome to an ogame bot. Paste espionaje report or type quit/q to quit.'
    ogbot = bot.logic.ogameBot()
    mainLoop(ogbot)
