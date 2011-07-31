'''
Created on Jul 30, 2011

@author: eduard
'''

import db as database

class ogameBot():
    def __init__(self):
        self.db = database.ogameDB();
    def getRentability(self):
        rentability = []
        for id in self.db.get_planet_list():
            p1, p2 = self.db.query('select coord, home_coord from planet where planet_id={}'.format(id), 1)
            cres = self.get_current_resources(id)
            if (not cres):
                continue;
            else:
                m, c, d = cres
            dist = float(self.get_distance(p1, p2))
            weighted_score = round((m + 2*c + 3*d) / dist, 2)
            plain_score = round((m + c + d) / dist, 2)
            cargo_nr = round((m + c + d) / 50000.0, 2)
            rentability.append((p1, weighted_score, plain_score, cargo_nr))
        print 'Coordonates\tWeighted score\tPlain Score\tNr of cargos'
        for coord, wr, pr, ships in sorted(rentability, key=lambda y: y[1], reverse = True):
            print str(coord).ljust(15), str(wr).ljust(15), str(pr).ljust(15), str(ships)
    
    def calculate_production(self, coord_mask = None, check = False):
        if coord_mask:
            self.db.query("select planet_id from planet where coord like '{}';".format(coord_mask), 0);
        else:
            bot.cursor.execute('select planet_id from planet;');
        planet_list = [ id for id, in bot.cursor.fetchall() ]
        print 'Calculating production for {} planets'.format(len(planet_list))
        for id in planet_list:
            if bot.cursor.execute('select date, metal, crystal, deuterium from report where planet_id={} order by date desc;'.format(id)) < 2:
                print 'Need another report for planet {} to calculate production.'.format(id)
                continue
            x = bot.cursor.fetchall()
            
            dt = (x[0][0] - x[1][0]).total_seconds() / 3600.0
            r = [int(round(i)) for i in [(x[0][1] - x[1][1])/dt, (x[0][2] - x[1][2])/dt, (x[0][3] - x[1][3])/dt]]
            # check delta production, if it's too big raise an error 
            if check:
                bot.cursor.execute('select m_prod, c_prod, d_prod from planet where planet_id = {};'.format(id))
                r0 = [int(i) for i in bot.cursor.fetchone()]
                res = {0: 'metal', 1: 'crystal', 2: 'deuterium'}
                for i in range(3):
                    if r[i] < 0:
                        print 'Invalid production for planet {}'.format(bot.get_planet_coord(id))
                        print 'Leaving original as is'
                        r = r0
                        break
                    if abs(r0[i] - r[i]) / float(max(r0[i], r[i])) > 1.0/100.0:
                        print 'Warning! Too big a difference in production for resourse {} on planet {}'.format(res[i], bot.get_planet_coord(id))
                        print 'Original was {}, new production is {}. Leaving original as is.'.format(r0[i], r[i])
                        r[i] = r0[i]
            bot.cursor.execute('update planet set m_prod={}, c_prod={}, d_prod={} where planet_id = {};'.format(r[0], r[1], r[2], id))
