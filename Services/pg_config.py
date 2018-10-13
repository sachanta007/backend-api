import psycopg2

class PgConfig:
	@staticmethod
	def db():
		try:
			conn = psycopg2.connect("dbname='brevwdnu' user='brevwdnu' host='elmer.db.elephantsql.com' password='fHFLQnWQe4e5OB3Bfx1oIxkPLtwl1Gev'")
			return conn
		except:
			return False
