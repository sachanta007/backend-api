from Services.pg_config import PgConfig
from Services.email_config import Email
from Services.crypto import Crypto
from Services.jwt import Jwt
from random import randint

class Service:

	@staticmethod
	def register(app, user):
		cur = None
		conn = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				password = Crypto.encrypted_string(user['password'])

				register_query = "INSERT INTO users(first_name,last_name, email, password, \
				security_question, security_answer, status) VALUES (%s, %s, %s, %s,%s,%s, %s)"
				cur.execute(register_query, (user['firstName'], user['lastName'], \
					user['email'], password, user['securityQuestion'], user['securityAnswer'], 'deactive'));
				conn.commit()

				email = Email(to=user['email'], subject='Welcome to Course 360')
				ctx = {'username': user['firstName'], 'url':'http://localhost:5000/activate/'+user['email']}
				email.html('confirmRegistration.html', ctx)
				email.send()

				cur.close()
				conn.close()

				return True
			else:
				return "Unable to connect"
		except Exception as e:
			return  e
		finally:
				cur.close()
				conn.close()

	@staticmethod
	def activate_user(email):
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()

				update_query = "UPDATE users SET status = %s WHERE users.email LIKE %s"
				cur.execute(update_query, ('activate', email));

				conn.commit()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
			return {"Error": e}
		finally:
				cur.close()
				conn.close()

	@staticmethod
	def login(email, password):
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				login_query = "SELECT users.password, users.user_id AS password \
				FROM users WHERE users.email LIKE %s"
				cur.execute(login_query, (email, ))
				user = cur.fetchone()
				response = {'token':'', 'email':''}
				if(Crypto.verify_decrypted_string(password, user[0])):
					response['token'] = str(Jwt.encode_auth_token(user_id=user[1]))
					response['email']= email
					return response
					#status = Jwt.decode_auth_token(token)
				else:
					return "Not able to login"
			else:
				return "Invalid Email or Password"

		except Exception as e:
			print(e)
			return {"Error occured": e}

		finally:
				cur.close()
				conn.close()

	@staticmethod
	def security_question(email):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()

				select_query = "SELECT security_question FROM users WHERE email LIKE %s"
				cur.execute(select_query, (email,))
				question = cur.fetchone()[0]

				if(question):
					return question
				else:
					return "Question not found"
			else:
				return "Unable to connect"
		except Exception as e:
			return e
		finally:
				cur.close()
				conn.close()

	@staticmethod
	def generate_random_number(n):
	    range_start = 10**(n-1)
	    range_end = (10**n)-1
	    return randint(range_start, range_end)

	@staticmethod
	def send_otp(email, answer):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				select_query = "SELECT users.security_answer, users.first_name FROM users WHERE users.email LIKE %s"
				cur.execute(select_query, (email,))
				result = cur.fetchone()
				security_answer = result[0]
				if(security_answer):
					if(answer == security_answer):
						otp = Service.generate_random_number(6)
						update_query = "UPDATE users SET otp = %s WHERE users.email LIKE %s"
						cur.execute(update_query, (otp,email,))
						conn.commit()

						email = Email(to=email, subject='Welcome to Course 360')
						ctx = {'username': result[0], 'otp': otp}
						email.html('otp.html', ctx)
						email.send()

						return True
					else:
						return "Wrong answer"
				else:
					return "Invalid request"
			else:
				return "Unable to connect"
		except Exception as e:
			print(e)
			return e
		finally:
				cur.close()
				conn.close()
