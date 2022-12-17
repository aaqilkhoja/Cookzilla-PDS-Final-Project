from flask import Flask


UPLOAD_FOLDER = 'FlaskDemoPhotos'

app = Flask(__name__)
app.secret_key = "keythatyouwontknowwwwww@@@@@@"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
