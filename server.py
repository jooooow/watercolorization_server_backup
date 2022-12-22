#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import datetime
import random
import os
import re
import glob
import time
import random
from flask import Flask, render_template
from flask import request, jsonify
from flask_socketio import SocketIO, emit

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

socketio = SocketIO()
socketio.init_app(app, cors_allowed_origins='*')
name_space = '/dcenter'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    sid = request.form['sid']
    file = request.files['img_file']
    file.save(UPLOAD_FOLDER + "/" + sid + "_" + file.filename)
    return "200"

@socketio.on('connect', namespace=name_space)
def connected_msg():
    sid = request.sid
    print(f'client connected to {sid}')
    event_name = 'dcenter'
    data = {'sid': sid}
    socketio.emit(event_name, data, room=sid, namespace=name_space)

@socketio.on('disconnect', namespace=name_space)
def disconnect_msg():
    sid = request.sid
    print(f'client disconnected from {sid}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234)