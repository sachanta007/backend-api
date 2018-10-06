from Services.pg_config import PgConfig
from Services.email_config import Email
from Services.crypto import Crypto
from Services.jwt import Jwt

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
				insert_query = "INSERT INTO courses(course_id, course_name, description, prof_id, location,\
				start_time, end_time, days, department) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

				cur.execute(insert_query, (courses['course_id'], courses['course_name'], courses['description'], \
				courses['prof_id'], courses['location'], courses['start_time'], courses['end_time'], \
				courses['days'], courses['department'], ));

				conn.commit()
				cur.close()
				conn.close()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
				print(e)
				return  e


	@staticmethod
	def update_password(data):
		cur = None
		conn = None
		try:
			conn = PgConfig.db()
			if (conn):
				cur = conn.cursor()
				check_otp = "SELECT users.otp AS otp \
				FROM users WHERE users.email LIKE %s"
				cur.execute(check_otp , (data['email'],))
				otp = cur.fetchone()[0]

				if(otp):
					if (pas == otp):
						update_password = "UPDATE  users SET users.password = %s where users.email LIKE %s"
						cur.execute(update_password, (data['password'],data['email'], ));
						conn.commit()
						conn.close()
						return True
					else:
						return "Invalid OTP"
			else:
					return " Something went wrong"
		except Exception as e:
			print(e)
			return {"Error occured": e}




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
