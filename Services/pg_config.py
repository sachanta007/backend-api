import psycopg2

class PgConfig:
	@staticmethod
	def db():
		try:
			conn = psycopg2.connect("dbname='d1osp41mpkgnb' user='eswrjkcmucapvr' host='ec2-174-129-221-240.compute-1.amazonaws.com' password='1063d5172fb023493e422a7a8ee24413b9da962aa8441d785a5e0bf5cf72d573'")
			#psycopg2.connect("dbname='brevwdnu' user='brevwdnu' host='elmer.db.elephantsql.com' password='fHFLQnWQe4e5OB3Bfx1oIxkPLtwl1Gev'")
			return conn
		except:
			return False
