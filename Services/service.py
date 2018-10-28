from Services.pg_config import PgConfig
from Services.email_config import Email
from Services.crypto import Crypto
from Services.jwt import Jwt
from Models.User import User
from Models.Course import Course

from random import randint
import datetime

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
				courses.days, courses.department, courses.course_code FROM courses ORDER BY courses.course_name ASC LIMIT %s OFFSET %s"
				cur.execute(query, (end, start,))
				courses = cur.fetchall()
				course_list = []
				if(len(courses)):
					for response in courses:
						course = Course()
						course.course_id = response[0]
						course.course_name = response[1]
						course.description = response[2]
						course.professor = Service.get_user_by(response[3])
						course.location = response[4]
						course.start_time = response[5]
						course.end_time = response[6]
						course.days = response[7]
						course.department = response[8]
						course.course_code = response[9]
						course.comment = Service.get_comment_by(response[0])
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
				cur.execute(delete_query, (courses['course_id'],))

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
				start_time = %s, end_time = %s, days = %s, department = %s, course_code= %s WHERE  courses.course_id = %s"
				cur.execute(update_query, (courses['course_name'], courses['description'], \
				courses['prof_id'], courses['location'], courses['start_time'], courses['end_time'], \
				courses['days'], courses['department'], courses['course_code'], courses['course_id'], ));

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
				start_time, end_time, days, department, course_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

				cur.execute(insert_query, (courses['course_name'], courses['description'], \
				courses['prof_id'], courses['location'], courses['start_time'], courses['end_time'], \
				courses['days'], courses['department'], courses['course_code'], ));

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
				ctx = {'username': user['firstName'], 'url':'http://course360.herokuapp.com/activate/'+user['email']}
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
	def authenticate(data):
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				login_query = "SELECT users.password, users.user_id, users.first_name AS password \
				FROM users WHERE users.email LIKE %s"
				cur.execute(login_query, (data['email'], ))
				user = cur.fetchone()
				if(Crypto.verify_decrypted_string(data['password'], user[0])):
					otp = Service.generate_random_number(6)
					update_query = "UPDATE users SET otp = %s WHERE users.email LIKE %s"
					cur.execute(update_query, (otp,data['email'],))
					conn.commit()
					email = Email(to=data['email'], subject='Login OTP')
					ctx = {'username': user[2], 'otp': otp, 'purpose':'This OTP is generated to login to the application'}
					email.html('otp.html', ctx)
					email.send()
					return True
				else:
					return "Invalid Email or Password"
			else:
				return "Not able to connect"
		except Exception as e:
			raise e

	@staticmethod
	def login(data):
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				login_query = "SELECT users.otp, users.user_id AS password \
				FROM users WHERE users.email LIKE %s"
				cur.execute(login_query, (data['email'], ))
				user = cur.fetchone()
				response = User()
				if(user[0]==data['otp']):
					response.email= data['email']
					response.user_id = user[1]
					get_role_query = "SELECT user_role.role_id FROM user_role WHERE user_role.user_id = %s"
					cur.execute(get_role_query, (user[1],))
					response.role_id = cur.fetchone()[0]
					response.token = (Jwt.encode_auth_token(user_id=user[1], role_id=response.role_id)).decode()
					cur.close()
					conn.close()
					return response
				else:
					return False
			else:
				return False
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
						ctx = {'username': result[1], 'otp': otp, 'purpose':"This OTP is generated to change your account's password"}
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
					user.user_id = id
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
				query = "SELECT course_id, course_name, description, prof_id, location, start_time, end_time, days, department,\
				course_code FROM courses WHERE course_name ILIKE %s ORDER BY course_name LIMIT %s OFFSET %s"
				cur.execute(query, (name+'%', end, start,))
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
						course.comment = Service.get_comment_by(obj[0])
						course.course_code = obj[9]
						courses_list.append(course)
					cur.close()
					conn.close()
					return courses_list
				else:
					cur.close()
					conn.close()
					return []

		except Exception as e:
			return e

	# Used from https://stackoverflow.com/questions/6558535/find-the-date-for-the-first-monday-after-a-given-a-date
	@staticmethod
	def next_weekday(d, weekday):
	    days_ahead = weekday - d.weekday()
	    if(days_ahead <= 0):
	        days_ahead += 7
	    return d + datetime.timedelta(days_ahead)

	@staticmethod
	def get_start_dates(days_occur):
		d = datetime.date(2018, 8, 19)
		next_monday = Service.next_weekday(d, 0)
		start_dates =[]
		for day in days_occur:
			weekday_date = next_monday + datetime.timedelta(days=(day-1))
			start_dates.append(str(weekday_date))
		return start_dates

	@staticmethod
	def get_professor_schedule(id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT course_name, start_time, end_time, location, course_id,\
				prof_id, days FROM courses WHERE prof_id = %s"
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
						course.days = schedule[6]
						course.start_dates =Service.get_start_dates(schedule[6])
						courses_list.append(course)
						cur.close()
						conn.close()
					return courses_list
				else:
					cur.close()
					conn.close()
					return []
		except Exception as e:
			return e

	@staticmethod
	def add_to_cart(course):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				insert_query = "INSERT INTO cart(user_id, course_id) VALUES (%s, %s)"
				cur.execute(insert_query, (course['user_id'], course['course_id'],));
				conn.commit()
				cur.close()
				conn.close()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
				return  e

	@staticmethod
	def get_cart(id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT courses.course_id,courses.course_name, courses.description, \
				courses.prof_id, courses.location, courses.start_time, courses.end_time, \
				courses.days, courses.department, courses.course_code FROM courses WHERE \
				course_id IN (SELECT course_id FROM cart where user_id = %s)"
				cur.execute(query, (id,))
				courses = cur.fetchall()
				course_list = []
				if(len(courses)):
					for response in courses:
						course = Course()
						course.course_id = response[0]
						course.course_name = response[1]
						course.description = response[2]
						course.professor = Service.get_user_by(response[3])
						course.location = response[4]
						course.start_time = response[5]
						course.end_time = response[6]
						course.days = response[7]
						course.department = response[8]
						course.course_code = response[9]
						course.user_id = id
						course_list.append(course)
				else:
					return []
				cur.close()
				conn.close()
				return course_list
		except Exception as e:
			return e

	@staticmethod
	def delete_from_cart(course_id, user_id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				delete_query = "DELETE FROM cart WHERE cart.course_id = %s AND cart.user_id = %s"
				cur.execute(delete_query, (course_id, user_id,));
				conn.commit()
				cur.close()
				conn.close()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
			return  e

	@staticmethod
	def save_comment(data):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				insert_query = "INSERT INTO course_comments(user_id, course_id, comment, course_ratings) VALUES (%s, %s, %s, %s)"
				cur.execute(insert_query, (data['user_id'], data['course_id'], data['comment'],data['ratings'],));
				conn.commit()
				cur.close()
				conn.close()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
				return  e

	@staticmethod
	def get_comment_by(course_id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT comment, user_id, course_ratings FROM course_comments WHERE course_id = %s"
				cur.execute(query, (course_id, ))
				comments = cur.fetchall()
				comment_list =[]
				for comment in comments:
					user = User()
					query = "SELECT first_name, last_name, email, user_id FROM users WHERE user_id = %s"
					cur.execute(query, (comment[1], ))
					response = cur.fetchone()
					user = User()
					user.first_name = response[0]
					user.last_name = response[1]
					user.email = response[2]
					user.user_id = response[3]
					user.comment= comment[0]
					user.rating = comment[2]
					comment_list.append(user)

				cur.close()
				conn.close()
				return comment_list
			else:
				cur.close()
				conn.close()
				return []

		except Exception as e:
			return e

	@staticmethod
	def get_course_by_id(course_id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT course_id, course_name, description, prof_id, location, start_time, end_time, days, department,\
				course_code FROM courses WHERE course_id = %s"
				cur.execute(query, (course_id,))
				obj = cur.fetchone()
				if(obj):
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
					course.comment = Service.get_comment_by(obj[0])
					course.course_code = obj[9]
					cur.close()
					conn.close()
					return course
				else:
					cur.close()
					conn.close()
					return []

		except Exception as e:
			return e
