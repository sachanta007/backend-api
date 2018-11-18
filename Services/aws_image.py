import base64
import boto
from boto.s3.key import Key
from boto.s3.connection import OrdinaryCallingFormat

class AwsImageHandler:
    @staticmethod
    def upload_image(img_str, img_name):
        AWS_ACCESS_KEY = 'AKIAIFCVURCK6MYMZOQQ'
        AWS_ACCESS_SECRET_KEY = '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'
        try:
            conn = boto.s3.connect_to_region('us-east-1',aws_access_key_id=AWS_ACCESS_KEY,aws_secret_access_key=AWS_ACCESS_SECRET_KEY,is_secure=False,calling_format=OrdinaryCallingFormat())

            bucket_name = 'course-360'

            bucket = conn.get_bucket('course-360',validate=False)
            k = Key(bucket)
            k.key = img_name
            temp = img_str.split(",",1)
            img_str = temp[1]
            decode_img = base64.b64decode(img_str)
            k.set_metadata('Content-Type', 'image/jpeg')
            k.set_contents_from_string(decode_img)
            k.make_public()
            return True
        except Exception as e:
            raise e
