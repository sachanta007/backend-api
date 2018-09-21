from flask import Flask,g,request,json,render_template


app = Flask(__name__, static_url_path='/static') #in order to access any images
app.config.from_object(__name__)

# app = Flask(__name__)
# app.config.from_object(__name__)
@app.route("/")
def check():
	#return "Hello"
	render_template('ex.html')

if __name__ == '__main__':
    #app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
