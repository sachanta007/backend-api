import jwt
from flask import Flask,g,request,json,render_template
from datetime import datetime
class Jwt:
	@staticmethod
	def encode_auth_token(user_id):
	    try:
	        payload = {
	            'sub': user_id
	        }
	        return jwt.encode(
	            payload,
	            'Course-360',
	            algorithm='HS256'
	        )
	    except Exception as e:
	        return e


	@staticmethod
	def decode_auth_token(auth_token):
	    try:
	        payload = jwt.decode(auth_token, 'Course-360')
	        return payload['sub']
	    except jwt.ExpiredSignatureError:
	        return 'Signature expired. Please log in again.'
	    except jwt.InvalidTokenError:
	        return 'Invalid token. Please log in again.'
