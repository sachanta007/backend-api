from passlib.context import CryptContext

class Crypto:

	@staticmethod
	def encrypted_string(text):
		pwd_context = CryptContext( schemes=["pbkdf2_sha256"], default="pbkdf2_sha256", pbkdf2_sha256__default_rounds=30000)
		return pwd_context.hash(text)
		

	@staticmethod
	def verify_decrypted_string(text, hashed):
		pwd_context = CryptContext( schemes=["pbkdf2_sha256"], default="pbkdf2_sha256", pbkdf2_sha256__default_rounds=30000)
		return pwd_context.verify(text, hashed)
