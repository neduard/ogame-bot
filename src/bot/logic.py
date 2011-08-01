'''
Created on Jul 30, 2011

@author: eduard
'''

import db as database

class ogameBot():
    def __init__(self):
        self.db = database.ogameDB();
    
    def __del__(self):
        print "ogameBot shutting down..."
        self.db.close()
    
    
    def get_distance(self, p1, p2):
        p1 = [int(i) for i in p1.split(':')]
        p2 = [int(i) for i in p2.split(':')]
        if p1[0] != p2[0]: return 20000
        elif p1[1] != p2[1]: return 2700 + abs(p1[1] - p2[1]) * 95
        else: return 1000 + abs(p1[2] - p2[2])
        
    def getRentability(self):
        rentability = []
        for id in self.db.get_planet_list():
            p1, p2 = self.db.query('select coord, home_coord from planet where planet_id={}'.format(id), 1)[0]
            cres = self.db.get_current_resources(id)
            if (not cres):
                continue;
            else:
                m, c, d = cres
            dist = float(self.get_distance(p1, p2))
            weighted_score = round((m + 2*c + 3*d) / dist, 2)
            plain_score = round((m + c + d) / dist, 2)
            cargo_nr = round((m + c + d) / 50000.0, 2)
            rentability.append((p1, weighted_score, plain_score, cargo_nr))
        return rentability

    
    def calculate_production(self, coord_mask = None, check = False):
        # FIXME: set default coord_mask to % ? (thus eliminating the if coord_mask) 

        if coord_mask:
            dbq = "select planet_id from planet where coord like '{}';".format(coord_mask)
        else:
            dbq = "select planet_id from planet;"
        
        planet_list = [ id for id, in self.db.query(dbq) ]
        print 'Calculating production for {} planets'.format(len(planet_list))
        for id in planet_list:
            x = self.db.query('select date, metal, crystal, deuterium from report where planet_id={} order by date desc;'.format(id), 2)
            if len(x) < 2:
                print 'Need another report for planet {} to calculate production.'.format(id)
                continue
            
            dt = (x[0][0] - x[1][0]).total_seconds() / 3600.0
            r = [int(round(i)) for i in [(x[0][1] - x[1][1])/dt, (x[0][2] - x[1][2])/dt, (x[0][3] - x[1][3])/dt]]
            # check delta production, if it's too big raise an error 
            if check:
                r0 = [ int(i) for i in self.db.query('select m_prod, c_prod, d_prod from planet where planet_id = {};'.format(id), 1)[0] ]
                res = {0: 'metal', 1: 'crystal', 2: 'deuterium'}
                for i in range(3):
                    if r[i] < 0:
                        print 'Invalid production for planet {}'.format(self.db.get_planet_coord(id))
                        print 'Leaving original as is'
                        r = r0
                        break
                    if abs(r0[i] - r[i]) / float(max(r0[i], r[i])) > 1.0/100.0:
                        print 'Warning! Too big a difference in production for resourse {} on planet {}'.format(res[i], self.db.get_planet_coord(id))
                        print 'Original was {}, new production is {}. Leaving original as is.'.format(r0[i], r[i])
                        r[i] = r0[i]
            self.db.query('update planet set m_prod={}, c_prod={}, d_prod={} where planet_id = {};'.format(r[0], r[1], r[2], id), 0)
