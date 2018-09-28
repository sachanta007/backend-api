
from flask import Flask,g,request,json,render_template,jsonify
from Services.service import Service

app = Flask(__name__, static_url_path='/static') #in order to access any images
app.config.from_object(__name__)

# app = Flask(__name__)
# app.config.from_object(__name__)
@app.route("/login", methods=['POST'])
def check():
	data = request.json
	try:
		response = Service.login(data['email'], data['password'])
		if (response):
			return jsonify(response), 200
		else:
			return jsonify({'Error': response}), 500
	except Exception as e:
		return jsonify(e), 500

@app.route("/register", methods=['POST'])
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
def activate_user(email):
	try:
		response = Service.activate_user(email)
		if(response == True):
			return jsonify({'data': 'Your account is activated'}), 200
		else:
			return jsonify({'Error': "response"}), 500
	except Exception as e:
		return  jsonify(e), 500

@app.route("/securityQuestion/<email>", methods=['GET'])
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

if __name__ == '__main__':
    #app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
