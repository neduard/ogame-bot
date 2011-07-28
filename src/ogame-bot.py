#! /usr/bin/python
import MySQLdb, re, datetime

class planet:
	def __init__(self, coord):
		self.galaxy, self.system, self.place = coord.split(':')
	def getCoord(self):
		return "{}:{}:{}".format(self.galaxy, self.system, self.place)

class ogameDB:
	def __init__(self):
		self.conn = MySQLdb.connect( host = "127.0.0.1",
                    user = "eduard",
                    passwd = "edi",
                    db = "ogame" )
		self.cursor = self.conn.cursor()
	
	def close(self):
		self.cursor.close()
		self.conn.close()
		
	def addPlanet(self, coord, home_planet = "2:109:10"):
		self.cursor.execute('insert into planet (coord, home_coord) value ("{}", "{}");'. format(coord, home_planet))
	
	def addReport(self, coord, datetime, metal, crystal, deuterium):
		dbquery = 'insert into report values (\
				  null, (select PLANET_ID from planet where coord="{}"),\
				  "{}", {}, {}, {});'.format(coord, datetime, metal, crystal, deuterium)
		if self.cursor.execute('select PLANET_ID from planet where coord="'+coord+'";') == 0:
			print "No planet with coordonates " + coord + " in database"
			print "Adding automatically..."
			self.addPlanet(coord);
		self.cursor.execute(dbquery)
	
	def get_distance(self, p1, p2):
		p1 = [int(i) for i in p1.split(':')]
		p2 = [int(i) for i in p2.split(':')]
		if p1[0] != p2[0]: return 20000
		elif p1[1] != p2[1]: return 2700 + abs(p1[1] - p2[1]) * 95
		else: return 1000 + abs(p1[2] - p2[2])
	
	def getRentability(self):
		self.cursor.execute('select planet_id from planet where m_prod is not null;')
		planet_list = [ id for id, in bot.cursor.fetchall() ]
		rentability = []
		for id in planet_list:
			self.cursor.execute('select date, metal, crystal, deuterium from report where planet_id={} order by date desc;'.format(id))
			row_report = [ i for i in self.cursor.fetchone() ]
			self.cursor.execute('select m_prod, c_prod, d_prod, coord, home_coord from planet where planet_id={}'.format(id))
			prod = [ i for i in self.cursor.fetchone() ]
			hours_passed = ((datetime.datetime.now() - datetime.timedelta(0,0,0,0,0,2)) - row_report[0]).seconds / 3600.0;
			current_res = 0
			for res in range(3):
				current_res += row_report[res + 1] + int(prod[res] * hours_passed)
			rentability.append((prod[3], round(float(current_res) / self.get_distance(prod[3], prod[4]), 2), current_res/50000.0))
		for coord, rent, ships in sorted(rentability, key=lambda y: y[1], reverse = True):
			print coord, rent, ships;
				

def parse_report(report):
	s = re.search('Resources at .* \[(.*)\] \(.*\) on (.*)', report[0])
	coord = s.group(1)
	date  = s.group(2)
	s = re.search("Metal:[\t ]*([0-9]+\.*[0-9]+)[\t ]*Crystal:[\t ]*([0-9]+\.*[0-9]+)", report[1])
	metal = s.group(1)
	crystal = s.group(2)
	s = re.search("Deuterium:[\t ]*([0-9]+\.*[0-9]+).*", report[2])
	deuterium = s.group(1)
	return coord, "2011-"+date, metal.replace('.', ''), crystal.replace('.', ''), deuterium.replace('.', '')
	
bot = ogameDB()

def calculate_production(bot, check = False):
	bot.cursor.execute('select planet_id from planet;');
	planet_list = [ id for id, in bot.cursor.fetchall() ]
	for id in planet_list:
		bot.cursor.execute('select date, metal, crystal, deuterium from report where planet_id={} order by date desc;'.format(id))
		x = bot.cursor.fetchall()
		dt = (x[0][0] - x[1][0]).total_seconds() / 3600.0
		r = [(x[0][1] - x[1][1])/dt, (x[0][2] - x[1][2])/dt, (x[0][3] - x[1][3])/dt]
		# check delta production, if it's too big raise an error 
		if check:
			bot.cursor.execute('select m_prod, c_prod, d_prod from planet where planet_id = {};'.format(id))
			r0 = [i for i in bot.cursor.fetchone()]
			res = {0: 'metal', 1: 'crystal', 2: 'deuterium'}
			for i in range(3):
				if abs(r0[i] - r[i]) / float(max(r0[i], r[i])) > 1.0/100.0:
					print 'Warning! Too big a difference in production for resourse {}'.format(res[i])
					print 'Original was {}, new production is {}. Leaving original as is.'.format(r0[i], r[i])
					r[i] = r0[i]
		bot.cursor.execute('update planet set m_prod={}, c_prod={}, d_prod={} where planet_id = {};'.format(r[0], r[1], r[2], id))

print 'Welcome to an ogame bot. Paste espionaje report or type quit/q to quit.'
while True:
	command = raw_input(">");
	if re.match('Resources at .*', command):
		report = [command, raw_input(), raw_input()]
		print "Processing report..."
		c, d, m, cr, de = parse_report(report)
		bot.addReport(c, d, m, cr, de)
	
	elif re.match('(?i)cprod', command):
		calculate_production(bot, re.match('cprod -c', command) != None)
		
	elif re.match('(?i)rent', command):
		bot.getRentability()
		
	elif re.match('(?i)(quit|q)\Z', command):
		print "Exiting..."
		break
	

bot.close();

