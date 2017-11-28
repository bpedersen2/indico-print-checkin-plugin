#/usr/bin/env python

from flask import Flask
from flask import request
from werkzeug.utils import secure_filename
import socket
#
config = {'printer': 'localhost'}

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Printer Proxy!'

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        sendToPrinter(f)
    return 'success'

@app.route('/json', methods=['GET', 'POST'])
def upload_json():
    if request.method == 'POST':
        data = request.get_json()
        print data
    return 'success'


def sendToPrinter(stream):
    try:
        printer = socket.socket()
        printer.connect((config['printer'], 9100))
        printer.send(stream)
        printer.close()
    except socket.error:
        return False
