
from Services.pg_config import PgConfig
from Services.email_config import Email
from Services.crypto import Crypto

class Service:

	@staticmethod
	def register(app, user):
		try:
			conn = PgConfig.db()
			if(conn):
				cur = conn.cursor()
				password = Crypto.encrypted_string(user['password'])
				
				register_query = "INSERT INTO users(first_name,last_name, email, password, \
				security_question, security_answer, status) VALUES (%s, %s, %s, %s,%s,%s, %s)"
				cur.execute(register_query, (user['firstName'], user['lastName'], \
					user['email'], password, user['securityQuestion'], user['securityAnswer'], 'deactive'));
				
				email = Email(to='sairohith.achanta@gmail.com', subject='Welcome to Course 360')  
				ctx = {'username': user['firstName'], 'url':'http://localhost:5000/activate/'+user['email']}  
				email.html('confirmRegistration.html', ctx)
				email.send() 
				
				conn.commit()
				return True
			else:
				return "Unable to connect"
		except Exception as e:
			return {"Error": "Couldn't register the user"}
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
				print("Hello")
				return "Unable to connect"
		except Exception as e:
			print(e)
			return {"Error": e}
		finally:
				cur.close()
				conn.close()