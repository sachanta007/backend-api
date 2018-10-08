from Services.pg_config import PgConfig
from Services.email_config import Email
from Services.crypto import Crypto
from Services.jwt import Jwt
from Models.User import User

from random import randint

class Service:

	@staticmethod
	def auth_token(token):
		return Jwt.decode_auth_token(token)

	@staticmethod
	def insert_courses(courses):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				insert_query = "INSERT INTO courses(course_name, description, prof_id, location,\
				start_time, end_time, days, department) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

				cur.execute(insert_query, (courses['course_name'], courses['description'], \
				courses['prof_id'], courses['location'], courses['start_time'], courses['end_time'], \
				courses['days'], courses['department'], ));

				conn.commit()
				cur.close()
				conn.close()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
				return  e


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
				security_question, security_answer, status) VALUES (%s, %s, %s, %s,%s,%s, %s) RETURNING user_id"
				cur.execute(register_query, (user['firstName'], user['lastName'], \
					user['email'], password, user['securityQuestion'], user['securityAnswer'], 'deactive'));
				user_id = cur.fetchone()[0]
				add_role_query = "INSERT INTO user_role(user_id, role_id) VALUES (%s, %s)"
				cur.execute(add_role_query, (user_id, user['role'],))

				email = Email(to=user['email'], subject='Welcome to Course 360')
				ctx = {'username': user['firstName'], 'url':'http://localhost:5000/activate/'+user['email']}
				email.html('confirmRegistration.html', ctx)
				email.send()

				conn.commit()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
			return e
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
	def login(data):
		try:
			conn = PgConfig.db()
			if(conn):

				cur = conn.cursor()
				login_query = "SELECT users.password, users.user_id AS password \
				FROM users WHERE users.email LIKE %s"
				cur.execute(login_query, (data['email'], ))
				user = cur.fetchone()
				response = User()
				if(Crypto.verify_decrypted_string(data['password'], user[0])):
					response.email= data['email']

					get_role_query = "SELECT user_role.role_id FROM user_role WHERE user_role.user_id = %s"
					cur.execute(get_role_query, (user[1],))
					response.role_id = cur.fetchone()[0]
					response.token = (Jwt.encode_auth_token(user_id=user[1], role_id=response.role_id)).decode()
					cur.close()
					conn.close()
					return response
				else:
					return "Not able to login"
			else:
				return "Invalid Email or Password"

		except Exception as e:
			raise e

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

	"""
	Checks whether answer input by user is same as that in DB
	for his/her email

	Returns True or False
	"""
	@staticmethod
	def verify_security_answer(answer_given,email):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()

				select_query = "SELECT security_answer FROM users WHERE email LIKE %s"
				cur.execute(select_query, (email,))
				actual_answer = cur.fetchone()[0]

				if(actual_answer == answer_given):
					return True
				else:
					return False
		except Exception as e:
			return e
		finally:
				cur.close()
				conn.close()

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

	@staticmethod
	def update_password(password, email):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "UPDATE users SET password = %s WHERE users.email LIKE %s"
				cur.execute(query, (Crypto.encrypted_string(password),email))
				if(cur.rowcount==1):
					conn.commit()
					return True
				else:
					print('Update Failed!!!!! Email not found, maybe???')
					return False

		except Exception as e:
			return e
		finally:
			cur.close()
			conn.close()

	@staticmethod
	def get_all_students(start, end):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT users.first_name, users.last_name, users.email FROM users,\
				(SELECT user_id FROM user_role WHERE role_id = %s) AS user_role \
				WHERE users.user_id = user_role.user_id LIMIT %s OFFSET %s"
				cur.execute(query, (3, end, start,))
				users = cur.fetchall()
				user_list = []
				if(len(users)):
					for response in users:
						user = User()
						user.first_name = response[0]
						user.last_name = response[1]
						user.email = response[2]
						user_list.append(user)
				else:
					return False

				cur.close()
				conn.close()
				return user_list
		except Exception as e:
			return e
