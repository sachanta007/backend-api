import boto.ses

AWS_ACCESS_KEY = 'AKIAIUZFCFTQ4YJ27IV'  
AWS_SECRET_KEY = 'bCVqc4oYTH9MXyCELEFYmxPLPhQ2cQPiE8cgBInI'

class Email(object):  
    def __init__(self, to, subject):
        self.to = to
        self.subject = subject
        self._html = None
        self._text = None
        self._format = 'html'

    def html(self, html):
        self._html = html

    def text(self, text):
        self._text = text

    def send(self, from_addr=None):
        body = self._html

        #if isinstance(self.to, basestring):
        #    self.to = [self.to]
        if not from_addr:
            from_addr = 'achantasairohith@gmail.com'
        if not self._html and not self._text:
            raise Exception('You must provide a text or html body.')
        if not self._html:
            self._format = 'text'
            body = self._text

        connection = boto.ses.connect_to_region(
            'us-east-1',
            aws_access_key_id='AKIAJAR4RJMB6DDV6HEA', 
            aws_secret_access_key='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'
        )

        return connection.send_email(
            from_addr,
            self.subject,
            None,
            self.to,
            format=self._format,
            text_body=self._text,
            html_body=self._html
        )