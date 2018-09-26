
import psycopg2

class PgConfig:
	@staticmethod
	def db():
		try:
			conn = psycopg2.connect("dbname='Course-360' user='postgres' host='localhost' password='1234'")
			return conn
		except:
			return False
		