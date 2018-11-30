from Services.pg_config import PgConfig
from Services.email_config import Email
from Services.crypto import Crypto
from Services.jwt import Jwt
from Services.aws_image import AwsImageHandler
from Models.User import User
from Models.Course import Course
from Models.Payment import Payment
from Models.semester_details import SemesterDetails
from random import randint
import datetime

class Service:

	@staticmethod
	def semesters():
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				select_query = "SELECT id, name, registration_start_date, registration_end_date, payment_end_date FROM semester_details"
				cur.execute(select_query)
				result = cur.fetchall()
				sem_list = []
				if(len(result)):
					for obj in result:
						sem = SemesterDetails()
						sem.sem_id = obj[0]
						sem.name = obj[1]
						sem.registration_start_date = obj[2]
						sem.registration_end_date = obj[3]
						sem.payment_end_date = obj[4]
						sem_list.append(sem)

				cur.close()
				conn.close()
				return sem_list
			else:
				return FALSE
		except Exception as e:
			return  e

	@staticmethod
	def get_sem_by(sem_id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				select_query = "SELECT id, name, registration_start_date, registration_end_date, payment_end_date FROM semester_details\
				WHERE id = %s"
				cur.execute(select_query,(sem_id,))
				obj = cur.fetchone()
				sem = SemesterDetails()

				if(len(obj)):
					sem.sem_id = obj[0]
					sem.name = obj[1]
					sem.registration_start_date = obj[2]
					sem.registration_end_date = obj[3]
					sem.payment_end_date = obj[4]

				cur.close()
				conn.close()
				return sem
			else:
				return FALSE
		except Exception as e:
			return  e

	@staticmethod
	def delete_comment(comment_id,course_id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				delete_query = "DELETE FROM course_comments WHERE  course_comments.comment_id = %s \
				and course_comments.course_id = %s"
				cur.execute(delete_query, (comment_id,course_id,))
				conn.commit()
				cur.close()
				conn.close()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
			return  e

	@staticmethod
	def send_receipt(email):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT users.first_name FROM users WHERE users.email LIKE %s"
				cur.execute(query, (email,))
				result = cur.fetchone()
				email = Email(to=email, subject='Payment Confirmation Receipt')
				ctx = {'username': result[0],'purpose':"Your payment is successful."}
				email.html('receipt.html', ctx)
				email.send()
				cur.close()
				conn.close()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
			return e

	@staticmethod
	def personal_details(users):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				AwsImageHandler.upload_image(users['image'], "u"+str(users['userId'])+".jpg")
				cur = conn.cursor()
				update_query = "UPDATE users SET first_name = %s, middle_name = %s, last_name = %s, dob = %s,\
				gender = %s, permanent_address = %s, present_address = %s, alt_email = %s, phone= %s , cgpa = %s, \
				course = %s, image = %s WHERE  users.user_id = %s"
				cur.execute(update_query, (users['firstName'], users['middleName'], users['lastName'], users['dob'],\
				users['gender'],users['permanentAddress'], users['presentAddress'], users['altEmail'], users['phone'],\
				users['cgpa'], users['course'],"https://s3.amazonaws.com/course-360/u"+str(users['userId'])+".jpg",users['userId'], ));
				conn.commit()
				cur.close()
				conn.close()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
			return  e

	@staticmethod
	def get_enrolled_courses(user_id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				select_query = "SELECT course_id, sem_id FROM enrolled_courses WHERE enrolled_courses.user_id = %s"
				cur.execute(select_query, (user_id,))
				response = cur.fetchall()
				courses_list=[]
				if(len(response)):
					for course in response:
						courses_list.append(Service.get_course_by_id(course[0], course[1]))

					cur.close()
					conn.close()
					return courses_list
				else:
					return False
			else:
				return "Unable to connect"
		except Exception as e:
			return  e

	@staticmethod
	def delete_enrolled_course(user_id, course_id, sem_id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				delete_query = "DELETE FROM enrolled_courses WHERE enrolled_courses.user_id = %s \
				and enrolled_courses.course_id = %s and enrolled_courses.sem_id = %s RETURNING payment"
				cur.execute(delete_query, (user_id,course_id,sem_id,))
				is_paid = cur.fetchone()[0]
				if(is_paid == 'true'):
					select_query = "SELECT finanical_aid FROM users WHERE user_id = %s"
					cur.execute(select_query, (user_id,))
					response = cur.fetchone()

					update_query = "UPDATE users SET finanical_aid=%s WHERE user_id = %s"
					cur.execute(update_query, (int(response[0])+ 650*3, user_id))
				conn.commit()
				cur.close()
				conn.close()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
			return  e

	@staticmethod
	def validate_courses(course1, course2):

		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			cur = conn.cursor()
			query1 = "SELECT courses.days, courses.start_time, courses.end_time FROM courses WHERE courses.course_id = %s"
			cur.execute(query1,(course1,))
			course1_days = cur.fetchone()
			query2 = "SELECT courses.days, courses.start_time, courses.end_time FROM courses WHERE courses.course_id = %s"
			cur.execute(query2,(course2,))
			course2_days = cur.fetchone()
			if(course1_days[0] != course2_days[0]):
				return True
			else:
				course1_start_time = course1_days[1]
				course2_start_time = course2_days[1]
				course1_end_time = course1_days[2]
				course2_end_time = course2_days[2]

				if(course1_start_time == course2_start_time):
					print("Timings of the selected courses clash, please select some other course")
					return False
				elif(course2_start_time <= course1_end_time):
					print("Timings of the selected courses clash, please select some other course")
					return False
				else:
					return True

		except Exception as e:
			return e

	@staticmethod
	def enroll_courses(data):
		conn = None
		cur = None
		user_id = data['user_id']
		sem_id = data['sem_id']
		try:
			conn = PgConfig.db()
			if(conn):
				payment = Payment()
				cur = conn.cursor()
				query = "SELECT cart.course_id, cart.sem_id from cart WHERE user_id = %s AND enrolled = 'false' AND sem_id = %s"
				cur.execute(query,(user_id, sem_id,))
				courses = cur.fetchall()
				course_status=[]
				for i in range(0, len(courses)-1):
					 for j in range(i+1, len(courses)):
						 course_status.append(Service.validate_courses(courses[i][0], courses[j][0]))

				payment = Payment()
				if(False in course_status):
					return False
				else:
					for course in courses:
						insert_query = "INSERT INTO enrolled_courses(user_id, course_id, sem_id) VALUES(%s, %s, %s)"
						cur.execute(insert_query, (user_id, course[0], course[1]))
						conn.commit()
						delete_from_cart_table = "DELETE FROM cart WHERE course_id = %s and user_id = %s and sem_id = %s"
						cur.execute(delete_from_cart_table, (course[0], user_id,sem_id,))
						conn.commit()
					payment.cost = 1300 * len(courses)
					finanical_aid_query = "SELECT finanical_aid FROM users WHERE user_id = %s"
					cur.execute(finanical_aid_query, (user_id,))
					obj = cur.fetchone()
					if(obj[0]):
						payment.finanical_aid = obj[0]
					else:
						payment.finanical_aid = Service.generate_random_number(3)
						update_query = "UPDATE users SET finanical_aid = %s WHERE users.user_id = %s"
						cur.execute(update_query, (payment.finanical_aid,user_id,))
						conn.commit()
					return payment
		except Exception as e:
			return e

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
				courses.days, courses.department, courses.course_code, courses.image FROM courses ORDER BY courses.course_name ASC LIMIT %s OFFSET %s"
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
						course.image = response[10]
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
				start_time = %s, end_time = %s, days = %s, department = %s, course_code= %s WHERE  courses.course_id = %s\
				RETURNING courses.image"
				cur.execute(update_query, (courses['course_name'], courses['description'], \
				courses['prof_id'], courses['location'], courses['start_time'], courses['end_time'], \
				courses['days'], courses['department'], courses['course_code'], courses['course_id'], ));
				old_img = cur.fetchone()[0]
				update_course = "UPDATE courses SET image = %s WHERE course_id = %s"
				if(courses['image']):
					AwsImageHandler.upload_image(courses["image"], str(courses['course_id'])+".jpg")
					cur.execute(update_course, ("https://s3.amazonaws.com/course-360/"+str(courses['course_id'])+".jpg",  courses['course_id'],))
					conn.commit()
				elif(not old_img):
					cur.execute(update_course, ("https://s3.amazonaws.com/course-360/cd.png",  courses['course_id'],))
					conn.commit()

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
				start_time, end_time, days, department, course_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING course_id"

				cur.execute(insert_query, (courses['course_name'], courses['description'], \
				courses['prof_id'], courses['location'], courses['start_time'], courses['end_time'], \
				courses['days'], courses['department'], courses['course_code'],));
				course_id = cur.fetchone()[0]
				img = "https://s3.amazonaws.com/course-360/cd.png"
				if('image' in courses and courses['image']):
					AwsImageHandler.upload_image(courses["image"], str(course_id)+".jpg")
					img = "https://s3.amazonaws.com/course-360/"+str(course_id)+".jpg"
				update_course = "UPDATE courses SET image = %s WHERE course_id = %s"
				cur.execute(update_course, (img, course_id,))
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
				security_question, security_answer, status, image) VALUES (%s, %s, %s, %s,%s,%s, %s, %s) RETURNING user_id"
				cur.execute(register_query, (user['firstName'], user['lastName'], \
					user['email'], password, user['securityQuestion'], user['securityAnswer'], 'deactive', "https://s3.amazonaws.com/course-360/user.jpg"));
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
				login_query = "SELECT users.otp, users.user_id, users.first_name, users.last_name, users.color_theme, users.image\
				FROM users WHERE users.email LIKE %s"
				cur.execute(login_query, (data['email'], ))
				user = cur.fetchone()
				response = User()
				if(user[0]==data['otp']):
					response.email= data['email']
					response.user_id = user[1]
					response.first_name = user[2]
					response.last_name = user[3]
					response.color_theme = user[4]
					response.image = user[5]
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
				query = "SELECT users.first_name, users.last_name, users.email, users.user_id, users.color_theme,\
				users.image, users.finanical_aid, users.cgpa FROM users, (SELECT user_id FROM user_role WHERE role_id = %s)\
				AS user_role WHERE users.user_id = user_role.user_id ORDER BY users.user_id LIMIT %s OFFSET %s"
				cur.execute(query, (role_id, end, start,))
				users = cur.fetchall()
				user_list = []
				if(len(users)):
					for response in users:
						user = User()
						user.first_name = response[0]
						user.last_name = response[1]
						user.full_name = ''
						if(response[0]):
							user.full_name = user.full_name + str(response[0])
						if(response[1]):
							user.full_name = user.full_name+' '+str(response[1])
						user.email = response[2]
						user.user_id = response[3]
						user.color_theme = response[4]
						user.image = response[5]
						user.finanical_aid = response[6]
						user.cgpa = response[7]
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
				query = "SELECT users.first_name, users.last_name, users.email, users.color_theme, users.image FROM users WHERE users.user_id = %s"
				cur.execute(query, (id,))
				obj = cur.fetchone()
				user =User()
				if(obj):
					user.first_name = obj[0]
					user.last_name = obj[1]
					user.email = obj[2]
					user.color_theme = obj[3]
					user.image = obj[4]
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
				course_code, image FROM courses WHERE course_name ILIKE %s ORDER BY course_name LIMIT %s OFFSET %s"
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
						course.image = obj[10]
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
				prof_id, days, course_code, department, description, image FROM courses WHERE prof_id = %s"
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
						course.course_code = schedule[7]
						course.comment = Service.get_comment_by(schedule[4])
						course.professor = Service.get_user_by(schedule[5])
						course.start_dates =Service.get_start_dates(schedule[6])
						course.department = schedule[8]
						course.description = schedule[9]
						course.image = schedule[10]
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
				insert_query = "INSERT INTO cart(user_id, course_id, sem_id) VALUES (%s, %s, %s)"
				cur.execute(insert_query, (course['user_id'], course['course_id'], course['sem_id']));
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
				courses.days, courses.department, courses.course_code, courses.image, sd.name, \
				sd.registration_start_date, sd.registration_end_date, sd.payment_end_date FROM courses,\
				(SELECT sem_id, course_id FROM cart WHERE user_id = 26) as cart, semester_details as sd\
				WHERE courses.course_id = cart.course_id AND sd.id = cart.sem_id;"
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
						course.image = response[10]
						sem = SemesterDetails()
						sem.sem_name = response[11]
						sem.registration_start_date = response[12]
						sem.registration_end_date = response[13]
						sem.payment_end_date = response[13]
						course.sem = sem
						course_list.append(course)
				else:
					return []
				cur.close()
				conn.close()
				return course_list
		except Exception as e:
			return e

	@staticmethod
	def delete_from_cart(course_id, user_id, sem_id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				delete_query = "DELETE FROM cart WHERE cart.course_id = %s AND cart.user_id = %s AND cart.sem_id = %s"
				cur.execute(delete_query, (course_id, user_id, sem_id));
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
					query = "SELECT first_name, last_name, email, user_id, color_theme, image FROM users WHERE user_id = %s"
					cur.execute(query, (comment[1], ))
					response = cur.fetchone()
					user = User()
					user.first_name = response[0]
					user.last_name = response[1]
					user.email = response[2]
					user.user_id = response[3]
					user.comment= comment[0]
					user.rating = comment[2]
					user.color_theme = response[4]
					user.image = response[5]
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
	def get_course_by_course_and_professor(course_id, professor_id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT course_id, course_name, description, prof_id, location, start_time, end_time, days, department,\
				course_code, image FROM courses WHERE course_id = %s AND prof_id = %s"
				cur.execute(query, (course_id, professor_id,))
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
					course.start_dates =Service.get_start_dates(obj[7])
					course.image = obj[10]
					cur.close()
					conn.close()
					return course
				else:
					cur.close()
					conn.close()
					return []

		except Exception as e:
			return e

	@staticmethod
	def get_course_by_id(course_id, sem_id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT course_id, course_name, description, prof_id, location, start_time, end_time, days, department,\
				course_code, image FROM courses WHERE course_id = %s"
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
					course.start_dates =Service.get_start_dates(obj[7])
					course.image = obj[10]
					course.sem = Service.get_sem_by(sem_id)
					cur.close()
					conn.close()
					return course
				else:
					cur.close()
					conn.close()
					return []

		except Exception as e:
			return e

	@staticmethod
	def check_fb_user_existence(email):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				select_query = "SELECT user_id, first_name, color_theme, image FROM users WHERE email LIKE %s AND type = %s"
				cur.execute(select_query, (email, 'fb', ));
				obj = cur.fetchone()
				response = User()
				if(obj):
					get_role = "SELECT role_id FROM user_role WHERE user_id = %s"
					cur.execute(get_role, (obj[0],));
					role = cur.fetchone()
					response.email= email
					response.user_id = obj[0]
					response.role_id = role[0]
					response.first_name = obj[1]
					response.color_theme = obj[2]
					response.image = obj[3]
					response.token = (Jwt.encode_auth_token(user_id=obj[0], role_id=response.role_id)).decode()
					cur.close()
					conn.close()
					return response
				else:
					cur.close()
					conn.close()
					return False
			else:
				return False
		except Exception as e:
			return  e

	@staticmethod
	def register_fb_user(data):
		cur = None
		conn = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()

				register_query = "INSERT INTO users(first_name, email, access_token, \
				type, status) VALUES (%s, %s, %s, %s, %s) RETURNING user_id"
				cur.execute(register_query, (data['firstName'], \
					data['email'], data['accessToken'], 'fb', 'active'));
				user_id = cur.fetchone()[0]
				add_role_query = "INSERT INTO user_role(user_id, role_id) VALUES (%s, %s)"
				cur.execute(add_role_query, (user_id, data['role'],))
				conn.commit()
				cur.close()
				conn.close()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
			return e

	@staticmethod
	def get_student_schedule(id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT courses.course_name, courses.start_time, courses.end_time, courses.location, courses.course_id, \
				courses.prof_id, courses.days, courses.course_code, courses.department, courses.description, courses.image FROM courses, \
				(SELECT course_id FROM enrolled_courses WHERE user_id = %s) as enrolled_courses \
				WHERE enrolled_courses.course_id = courses.course_id"
				cur.execute(query, (id,))
				schedules = cur.fetchall()
				courses_list = []
				if(len(schedules)):
					for schedule in schedules:
						course = Course()
						course.user_id = id
						course.course_name = schedule[0]
						course.start_time = schedule[1]
						course.end_time = schedule[2]
						course.location = schedule[3]
						course.course_id = schedule[4]
						course.prof_id = schedule[5]
						course.days = schedule[6]
						course.course_code = schedule[7]
						course.comment = Service.get_comment_by(schedule[4])
						course.professor = Service.get_user_by(schedule[5])
						course.start_dates =Service.get_start_dates(schedule[6])
						course.department = schedule[8]
						course.description = schedule[9]
						course.image = schedule[10]
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
	def get_students_by_course(id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "select user_id from enrolled_courses where course_id = %s"
				cur.execute(query, (id,))
				students = cur.fetchall()
				course = Service.get_course_by_id(id, None)
				students_list = []
				if(len(students)):
					for student in students:
						students_list.append(Service.get_user_by(student[0]))

					cur.close()
					conn.close()
					course.students = students_list
					return course
				else:
					cur.close()
					conn.close()
					return []
		except Exception as e:
			return e

	@staticmethod
	def get_students_by_course_and_professor(course_id, professor_id):
		conn = None
		cur = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				query = "SELECT user_id FROM enrolled_courses, (SELECT courses.course_id FROM courses \
				WHERE courses.course_id = %s AND courses.prof_id =%s) AS courses \
				WHERE courses.course_id = enrolled_courses.course_id"
				cur.execute(query, (course_id, professor_id))
				students = cur.fetchall()
				course = Service.get_course_by_course_and_professor(course_id, professor_id)
				students_list = []
				if(len(students)):
					for student in students:
						students_list.append(Service.get_user_by(student[0]))

					cur.close()
					conn.close()
					course.students = students_list
					return course
				else:
					cur.close()
					conn.close()
					return []
		except Exception as e:
			return e

	@staticmethod
	def update_financial_aid(value, student):
		cur = None
		conn = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				update_financial_aid_query = "UPDATE users SET finanical_aid = %s WHERE user_id = %s RETURNING user_id"
				cur.execute(update_financial_aid_query, (value, student,));
				user_id = cur.fetchone()[0]
				conn.commit()
				cur.close()
				conn.close()
				if(user_id):
					return True
				return False
			else:
				return "Unable to connect"
		except Exception as e:
			return e

	@staticmethod
	def update_color_theme(theme, student):
		cur = None
		conn = None
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				update_color_theme_query = "UPDATE users SET color_theme = %s WHERE user_id = %s RETURNING user_id"
				cur.execute(update_color_theme_query, (theme, student,));
				user_id = cur.fetchone()[0]
				conn.commit()
				cur.close()
				conn.close()
				if(user_id):
					return True
				return False
			else:
				return "Unable to connect"
		except Exception as e:
			return e
