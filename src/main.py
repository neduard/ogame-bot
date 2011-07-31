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
            ogbot.getRentability()
            
        elif re.match('gres', command):
            print 'current resources for all planets'
            for id in ogbot.get_planet_list():
                x = ogbot.get_current_resources(id)
                if (x[0]): print ogbot.get_planet_coord(id), x
            
        elif re.match('(quit|q)\Z', command):
            print "Exiting..."
            break
        
        else:
            print "Command not found. Only two command so far are cprod [-c] [coord_mask] and rent"    

if __name__ == '__main__':
    print 'Welcome to an ogame bot. Paste espionaje report or type quit/q to quit.'
    ogbot = bot.logic.ogameBot()
    mainLoop(ogbot)
    ogbot.close()
