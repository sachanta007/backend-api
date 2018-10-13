from Services.pg_config import PgConfig
from Services.email_config import Email
from Services.crypto import Crypto
from Services.jwt import Jwt
from Models.User import User
from Models.Course import Course

from random import randint

class Service:


	@staticmethod
	def get_all_courses(start, end):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT courses.course_id,courses.course_name, courses.description, \
				courses.prof_id, courses.location, courses.start_time, courses.end_time, \
				courses.days, courses.department FROM courses ORDER BY courses.course_name ASC LIMIT %s OFFSET %s"
				cur.execute(query, (end, start,))
				courses = cur.fetchall()
				course_list = []
				if(len(courses)):
					for response in courses:
						course = Course()
						course.course_id = response[0]
						course.course_name = response[1]
						course.description = response[2]
						course.prof_id = response[3]
						course.location = response[4]
						course.start_time = response[5]
						course.end_time = response[6]
						course.days = response[7]
						course.department = response[8]
						course_list.append(course)
				else:
					return []

				cur.close()
				conn.close()
				return course_list
		except Exception as e:
			return e


	@staticmethod
	def delete_courses(courses):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				delete_query = "DELETE FROM courses WHERE  courses.course_id = %s"
				cur.execute(delete_query,courses['course_id'],);

				conn.commit()
				cur.close()
				conn.close()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
			return  e


	@staticmethod
	def update_courses(courses):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				update_query = "UPDATE courses SET course_name = %s, description = %s, prof_id = %s, location = %s,\
				start_time = %s, end_time = %s, days = %s, department = %s WHERE  courses.course_id = %s"
				cur.execute(update_query, (courses['course_name'], courses['description'], \
				courses['prof_id'], courses['location'], courses['start_time'], courses['end_time'], \
				courses['days'], courses['department'], courses['course_id'],));

				conn.commit()
				cur.close()
				conn.close()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
			return  e

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
				cur.close()
				conn.close()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
			return e

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
	def get_all(users, start, end):
		conn = None
		cur = None
		role_id = 3 #default to students
		if(users=="PROFESSORS"):
			role_id = 2
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT users.first_name, users.last_name, users.email, users.user_id FROM users,\
				(SELECT user_id FROM user_role WHERE role_id = %s) AS user_role \
				WHERE users.user_id = user_role.user_id ORDER BY users.user_id LIMIT %s OFFSET %s"
				cur.execute(query, (role_id, end, start,))
				users = cur.fetchall()
				user_list = []
				if(len(users)):
					for response in users:
						user = User()
						user.first_name = response[0]
						user.last_name = response[1]
						user.email = response[2]
						user.user_id = response[3]
						user_list.append(user)
				else:
					return False

				cur.close()
				conn.close()
				return user_list
		except Exception as e:
			return e

	@staticmethod
	def get_user_by(id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT users.first_name, users.last_name, users.email FROM users WHERE users.user_id = %s"
				cur.execute(query, (id,))
				obj = cur.fetchone()
				user =User()
				if(obj):
					user.first_name = obj[0]
					user.last_name = obj[1]
					user.email = obj[2]
				else:
					return False
				cur.close()
				conn.close()
				return user
		except Exception as e:
			return e

	@staticmethod
	def get_course_by(name, start, end):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT course_id, course_name, description, prof_id, location, start_time, end_time, days, department\
				FROM courses WHERE course_name ILIKE %(like)s ESCAPE '=' ORDER BY course_name LIMIT %(end)s OFFSET %(end)s"
				cur.execute(query, (dict(like= name+'%',end= end, start= start)))
				courses = cur.fetchall()
				courses_list = []
				if(len(courses)):
					for obj in courses:
						course = Course()
						course.course_id=obj[0]
						course.course_name=obj[1]
						course.description=obj[2]
						course.location = obj[4]
						course.start_time = obj[5]
						course.end_time = obj[6]
						course.days = obj[7]
						course.department = obj[8]
						course.professor = Service.get_user_by(obj[3])
						courses_list.append(course)
				else:
					return []
				cur.close()
				conn.close()
				return courses_list
		except Exception as e:
			return e

	@staticmethod
	def get_professor_schedule(id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT course_name, start_time, end_time, location, course_id,\
				prof_id from courses where prof_id = %s"
				cur.execute(query, (id,))
				schedules = cur.fetchall()
				courses_list = []
				if(len(schedules)):
					for schedule in schedules:
						course = Course()
						course.course_name = schedule[0]
						course.start_time = schedule[1]
						course.end_time = schedule[2]
						course.location = schedule[3]
						course.course_id = schedule[4]
						course.prof_id = schedule[5]
						courses_list.append(course)
				else:
					return []
				cur.close()
				conn.close()
				return courses_list
		except Exception as e:
			return e
