import psycopg2

class PgConfig:
	@staticmethod
	def db():
		try:
			#local DB
			#conn = psycopg2.connect("dbname='Course-360' user='postgres' host='localhost' password='1234'")

			#Development Database
			conn = psycopg2.connect("dbname='d1osp41mpkgnb' user='eswrjkcmucapvr' host='ec2-174-129-221-240.compute-1.amazonaws.com' password='1063d5172fb023493e422a7a8ee24413b9da962aa8441d785a5e0bf5cf72d573'")

			#Production Database
			#conn = psycopg2.connect("dbname='d3254l0tko2mu3' user='vuhccmeedogeij' host='ec2-50-17-203-51.compute-1.amazonaws.com' password='3562f77f18869b299dc10acce105fd435a201ab50c646ab0a6eb33424240fc40'")

			#psycopg2.connect("dbname='brevwdnu' user='brevwdnu' host='elmer.db.elephantsql.com' password='fHFLQnWQe4e5OB3Bfx1oIxkPLtwl1Gev'")
			return conn
		except:
			return False
