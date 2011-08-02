'''
Created on Jul 29, 2011

@author: eduard
'''

import MySQLdb, datetime

class ogameDB(object):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.conn = MySQLdb.connect( host = "127.0.0.1",
                    user = "eduard",
                    passwd = "edi",
                    db = "ogame" )
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()
        
    def query(self, query, nrOfRows = -1):
        if not self.cursor.execute(query):
            if nrOfRows:     return None
            else:            return []
        
        if   not nrOfRows:   return []
        elif nrOfRows == 1:  return [ self.cursor.fetchone() ]
        elif nrOfRows == -1: return [ row for row in self.cursor.fetchall() ]
        elif nrOfRows > 0:   return [ row for row in self.cursor.fetchall() ][:nrOfRows]
        else:
            print "Invalid number of rows to return %d" % nrOfRows
            return None
        
    def addPlanet(self, coord, home_planet = None):
        if not home_planet:
            if coord[0] == "2": home_planet = "2:109:10"
            else: home_planet = "1:381:6"
        dbquery = 'insert into planet (coord, home_coord) value ("%s", "%s");' % (coord, home_planet)
        self.dbQuery(dbquery)
    
    # rep is tuple (coord, datetime, metal, crystal, deuterium)
    def addReport(self, rep):
        dbquery = 'insert into report values (\
                  null, (select PLANET_ID from planet where coord="%s"),\
                  "%s", %s, %s, %s);'% rep;
        coord = rep[0];
        if self.cursor.execute('select PLANET_ID from planet where coord="%s";' % coord) == 0:
            print "No planet with coordonates %s in database" % coord
            print "Adding automatically..."
            self.addPlanet(coord);
        self.query(dbquery)
    
    def addCombatReport(self, rep):
        coord = rep[0]
        row = self.query('select planet_id from planet where coord="%s"' % coord, 1)
        if not row:
            print "Planet with coords %s is not in database" % coord
            return None
        current_res = self.get_current_resources(int(row[0][0]))
        captured_res = row[2:]
        if (not current_res):
            return None
        
        for i in range(3):
            if (current_res[i] - captured_res[i] < 0):
                print 'More bounty than there was on planet? This is bad.'
                return None
        dbquery = 'insert into report values (\
                   null, (select PLANET_ID from planet where coord="%s"),\
                   str_to_date("%s", "%%d.%%m.%%Y %%H:%%i:%%s"), %s, %s, %s);' % \
                   (rep[:2],) + tuple([ current_res[i] - captured_res[i] for i in range(3) ])
        self.cursor.execute(dbquery)
    
    def get_planet_list(self, mask = "%"):
        return [ id for id, in self.query("SELECT planet_id FROM planet WHERE coord LIKE '%s' ORDER BY coord" % mask) ]
        
    def get_planet_coord(self, id):
        return self.query('select coord from planet where planet_id={}'.format(id), 1)[0][0]
        
    def get_current_resources(self, id):
        if self.cursor.execute('select date, metal, crystal, deuterium from report where planet_id=%d order by date desc;' % id) == 0:
            print 'Can not calculate current resources for planet %s' % self.get_planet_coord(id)
            return None
        report_row = [ field for field in self.cursor.fetchone() ]
        hours_passed = ((datetime.datetime.now() - datetime.timedelta(0,0,0,0,0,2)) - report_row[0]).seconds / 3600.0;
        if self.cursor.execute('select m_prod, c_prod, d_prod from planet where planet_id=%d and m_prod is not null' % id) == 0:
            print "We don't know the production for planet %s" % self.get_planet_coord(id)
            return None
        production = [ int(prod) for prod in self.cursor.fetchone() ]
        resources =  [ int(res) for res in report_row[1:] ]
        cres = []
        for res_type in range(3):
            cres.append(resources[res_type] + int(production[res_type] * hours_passed))
        return (cres[0], cres[1], cres[2])
        