from flask import Flask,g,request,json,render_template,jsonify, redirect
from Services.service import Service
from flask_cors import CORS,cross_origin
import jsonpickle
from Services.jwt import Jwt

app = Flask(__name__, static_url_path='/static') #in order to access any images
app.config.from_object(__name__)

# Below is to enable requests from other domains i.e, enable React to access these APIs
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


# app = Flask(__name__)
# app.config.from_object(__name__)

@app.route('/getEnrolledCourses/userId/<user_id>',methods=['GET'])
def get_enrolled_courses(user_id):
	auth_header = request.headers.get('Authorization')
	data = request.json
	try:
		status = Jwt.decode_auth_token(auth_header)
		if(status):
			response = Service.get_enrolled_courses(user_id)
			if(response):
				return jsonpickle.encode(response, unpicklable=False), 200
			else:
				return jsonify({'Error':"Something went wrong"}), 500
		else:
			return jsonify({"Error": "Invalid token"}), 500
	except Exception as e:
		return jsonify(e), 500


@app.route('/dropCourse/courseId/<course_id>/userId/<user_id>',methods=['GET'])
def drop_course(course_id, user_id):
	auth_header = request.headers.get('Authorization')
	data = request.json
	try:
		status = Jwt.decode_auth_token(auth_header)
		if(status):
			response = Service.delete_enrolled_course(user_id, course_id)
			if(response):
				return  jsonify({'Success':"Dropped the course"}), 200
			else:
				return jsonify({'Error':"Something went wrong"}), 500
		else:
			return jsonify({"Error": "Invalid token"}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route('/enrollCourses',methods=['POST'])
def enroll_courses():
	auth_header = request.headers.get('Authorization')
	data = request.json
	try:
		status = Jwt.decode_auth_token(auth_header)
		if(status):
			response = Service.enroll_courses(data)
			if(response):
				return jsonpickle.encode(response, unpicklable=False), 200
			else:
				return jsonify({'Error':"Something went wrong"}), 500
		else:
			return jsonify({"Error": "Invalid token"}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route('/getAllCourses/start/<start>/end/<end>')
@cross_origin()
def get_all_courses(start, end):
	auth_header = request.headers.get('Authorization')
	try:
		status = Jwt.decode_auth_token(auth_header)
		if(status):
			if(status['role'] == str(1)):
				response = Service.get_all_courses(start, end)
				if(response):
					return jsonpickle.encode(response, unpicklable=False), 200
				else:
					return jsonify({"Error": "Something went wrong"}), 500
			else:
				return jsonify({"Error": "Unauthorised"}), 500
		else:
				return jsonify({"Error": "Invalid token"}), 500
	except Exception as e:
		return jsonify(e), 500


@app.route("/deleteCourses", methods=['POST'])
def delete_courses():
	data = request.json
	try:
		token = request.headers.get('Authorization')
		if(Service.auth_token(token)):
			if(data['role_id'] == str(1)):
				response = Service.delete_courses(data)
				print(response)
				if( response == True):
					return jsonify({'data': data}), 200
				else:
					return jsonify({'Error':'Something went wrong'}), 500
			else:
				return jsonify({'Error': 'Unauthorized'}), 500
		else:
			return jsonify({'Error': 'Unauthorized'}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route("/updateCourses", methods=['POST'])
def update_courses():
	data = request.json
	try:
		token = request.headers.get('Authorization')
		if(Service.auth_token(token)):
			if(data['role_id'] == str(1)):
				response = Service.update_courses(data)
				print(response)
				if( response == True):
					return jsonify({'data': data}), 200
				else:
					return jsonify({'Error':'Something went wrong'}), 500
			else:
				return jsonify({'Error': 'Unauthorized'}), 500
		else:
			return jsonify({'Error': 'Unauthorized'}), 500
	except Exception as e:
		return jsonify(e), 500


@app.route("/insertCourses", methods=['POST'])
def insert_courses():
	data = request.json
	try:
		token = request.headers.get('Authorization')
		if(Service.auth_token(token)):
			if(data['role_id'] == str(1)):
				response = Service.insert_courses(data)
				if( response == True):
					return jsonify({'data': data}), 200
				else:
					return jsonify({'Error':'Something went wrong'}), 500
			else:
				return jsonify({'Error': 'Unauthorized'}), 500
		else:
			return jsonify({'Error': 'Unauthorized'}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route("/authenticate", methods=['POST'])
@cross_origin()
def authenticate():
	data = request.json
	try:
		response = Service.authenticate(data)
		if (response==True):
			return jsonpickle.encode(response, unpicklable=False), 200
		else:
			return jsonify({'Error': "Something Went Wrong"}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route("/login", methods=['POST'])
@cross_origin()
def check():
	data = request.json
	try:
		response = Service.login(data)
		if (response):
			return jsonpickle.encode(response, unpicklable=False), 200
		else:
			return jsonify({'Error': "Something Went Wrong"}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route("/register", methods=['POST'])
@cross_origin()
def register():
	try:
		data = request.json
		response = Service.register(app, data)

		if( response == True):
			return jsonify({'data': data}), 200
		else:
			return jsonify({'Error':response}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route("/activate/<email>", methods=['GET'])
@cross_origin()
def activate_user(email):
	try:
		response = Service.activate_user(email)
		if(response == True):
			#return redirect("http://course360.herokuapp.com/activated", code=200)
			return jsonify({'data': 'Your account is activated'}), 200
		else:
			return jsonify({'Error': "response"}), 500
	except Exception as e:
		return jsonify(e), 500


@app.route("/securityQuestion/<email>", methods=['GET'])
@cross_origin()
def security_question(email):
	try:
		response = Service.security_question(email)
		if(response):
			return jsonify({'question': response}), 200
		else:
			return jsonify({'Error':"response"}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route("/sendOtp/email/<email>/answer/<answer>", methods=['GET'])
def send_otp(email, answer):
	try:
		response = Service.send_otp(email, answer)
		if(response == True):
			return jsonify({'data': response}), 200
		else:
			return jsonify({'Error': response}), 500
	except Exception as e:
		return jsonify(e), 500

"""
Verifies user's answer and actual security answer in DB
"""

@app.route("/securityAnswer", methods=['POST'])
@cross_origin()
def verify_security_answer():
	try:
		data = request.json
		response = Service.verify_security_answer(data['answer'],data['email'])
		return jsonify({'wasAnswerCorrect': response}), 200
	except Exception as e:
		return jsonify(e), 500


"""
Sets a new password for particular user, provided email and new password
"""

@app.route("/updatePassword", methods=['POST'])
@cross_origin()
def update_password():
	try:
		data = request.json
		response = Service.update_password(data['password'],data['email'])
		return jsonify({'wasUpdateSuccessful': response}), 200
	except Exception as e:
		return jsonify(e), 500

@app.route('/getAllStudents/start/<start>/end/<end>')
@cross_origin()
def get_all_students(start, end):
	auth_header = request.headers.get('Authorization')
	try:
		status = Jwt.decode_auth_token(auth_header)
		if(status):
			if(status['role'] == str(1)):
				response = Service.get_all("STUDENTS", start, end)
				if(response):
					return jsonpickle.encode(response, unpicklable=False), 200
				else:
					return jsonify({"Error": "Something went wrong"}), 500
			else:
				return jsonify({"Error": "Unauthorised"}), 500
		else:
				return jsonify({"Error": "Invalid token"}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route('/getAllProfessors/start/<start>/end/<end>')
@cross_origin()
def get_all_professors(start, end):
	auth_header = request.headers.get('Authorization')
	try:
		status = Jwt.decode_auth_token(auth_header)
		if(status):
			if(status['role'] == str(1)):
				response = Service.get_all("PROFESSORS", start, end)
				if(response):
					return jsonpickle.encode(response, unpicklable=False), 200
				else:
					return jsonify({"Error": "Something went wrong"}), 500
			else:
				return jsonify({"Error": "Unauthorised"}), 500
		else:
				return jsonify({"Error": "Invalid token"}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route('/getCourseBy/name/<name>/start/<start>/end/<end>')
@cross_origin()
def get_course(name, start, end):
	auth_header = request.headers.get('Authorization')
	try:
		status = Jwt.decode_auth_token(auth_header)
		if(status):
			response = Service.get_course_by(name, start, end)
			if(response):
				return jsonpickle.encode(response, unpicklable=False), 200
			else:
				return jsonify({"Error": "Something went wrong"}), 500
		else:
				return jsonify({"Error": "Invalid token"}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route('/getProfessorSchedule/id/<id>')
@cross_origin()
def get_schedule(id):
	auth_header = request.headers.get('Authorization')
	try:
		status = Jwt.decode_auth_token(auth_header)
		if(status):
			response = Service.get_professor_schedule(id)
			if(response):
				return jsonpickle.encode(response, unpicklable=False), 200
			else:
				return jsonify({"Error": "Something went wrong"}), 500
		else:
				return jsonify({"Error": "Invalid token"}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route("/addToCart", methods=['POST'])
def add_to_cart():
	data = request.json
	try:
		token = request.headers.get('Authorization')
		if(Service.auth_token(token)):
			response = Service.add_to_cart(data)
			if( response == True):
				return jsonify({'data': data}), 200
			else:
				return jsonify({'Error':'Something went wrong'}), 500
		else:
			return jsonify({'Error': 'Unauthorized'}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route('/getCart/userId/<id>')
@cross_origin()
def get_cart(id):
	auth_header = request.headers.get('Authorization')
	try:
		status = Jwt.decode_auth_token(auth_header)
		if(status):
			response = Service.get_cart(id)
			if(response):
				return jsonpickle.encode(response, unpicklable=False), 200
			else:
				return jsonify({"Error": "Something went wrong"}), 500
		else:
				return jsonify({"Error": "Invalid token"}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route('/delete/course/<course>/fromCart/for/user/<user>')
@cross_origin()
def delete_from_cart(course, user):
	auth_header = request.headers.get('Authorization')
	try:
		status = Jwt.decode_auth_token(auth_header)
		if(status):
			response = Service.delete_from_cart(course, user)
			if(response):
				return jsonify({"response": "Success"}), 200
			else:
				return jsonify({"Error": "Something went wrong"}), 500
		else:
				return jsonify({"Error": "Invalid token"}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route("/commentOnACourse", methods=['POST'])
def save_comment():
	data = request.json
	try:
		token = request.headers.get('Authorization')
		if(Service.auth_token(token)):
			response = Service.save_comment(data)
			if( response == True):
				return jsonify({'data': data}), 200
			else:
				return jsonify({'Error':'Something went wrong'}), 500
		else:
			return jsonify({'Error': 'Unauthorized'}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route('/getCourseBy/course/<course_id>')
@cross_origin()
def get_course_by(course_id):
	auth_header = request.headers.get('Authorization')
	try:
		status = Jwt.decode_auth_token(auth_header)
		if(status):
			response = Service.get_course_by_id(course_id)
			if(response):
				return jsonpickle.encode(response, unpicklable=False), 200
			else:
				return jsonify({"Error": "Something went wrong"}), 500
		else:
				return jsonify({"Error": "Invalid token"}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route('/checkFbUserExistence/email/<email>')
@cross_origin()
def check_fb_user_existence(email):
	try:
		response = Service.check_fb_user_existence(email)
		if(response):
			return jsonpickle.encode(response, unpicklable=False), 200
		else:
			return jsonify({"Error": "Something went wrong"}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route('/registerFbUser', methods=['POST'])
@cross_origin()
def register_fb_user():
	data = request.json
	try:
		response = Service.register_fb_user(data)
		if(response):
			response = Service.check_fb_user_existence(data['email'])
			return jsonpickle.encode(response, unpicklable=False), 200
		else:
			return jsonify({"Error": "Something went wrong"}), 500
	except Exception as e:
		return jsonify(e), 500




if __name__ == '__main__':
    #app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
