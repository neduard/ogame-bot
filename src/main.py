#! /usr/bin/python
'''
Created on Jul 29, 2011

@author: eduard
'''

import re, bot.logic, bot.parsers

def mainLoop(ogbot):
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
            
        # FIXME: not happy w/ current regex
        elif re.match('cprod', command):
            m = re.match('cprod ?(-c ?)?(.*)', command)
            coord = m.group(2)
            ogbot.calculate_production(coord, re.search('-c', command) != None)
            
        elif re.match('rent', command):
            print 'Coordonates\tWeighted score\tPlain Score\tNr of cargos'
            for coord, wr, pr, ships in sorted(ogbot.getRentability(), key=lambda y: y[1], reverse = True):
                print str(coord).ljust(15), str(wr).ljust(15), str(pr).ljust(15), str(ships)
            
        elif re.match('gres', command):
            print 'Current resources for all planets:'
            for id in ogbot.db.get_planet_list():
                x = ogbot.db.get_current_resources(id)
                if (x): print "%s %d %d %d" % (ogbot.db.get_planet_coord(id) + x)
            
        elif re.match('(d|del|delete)', command):
            x = re.match("(d|del|delete) ([1-9]:[1-9][0-9]{0,2}:[1-9][0-9]?)\Z", command)
            if (x):
                print "Delete planet %s" % x.group(2)
                ogbot.db.delete_planet(x.group(2))
            else: print "Bad coordinates. Format is 1:123:12"
            
        elif re.match('(quit|q)\Z', command):
            break
        else:
            print "Command not found. Only two command so far are cprod [-c] [coord_mask] and rent and gres"    

if __name__ == '__main__':
    print 'Welcome to an ogame bot. Paste espionaje report or type quit/q to quit.'
    ogbot = bot.logic.ogameBot()
    mainLoop(ogbot)
