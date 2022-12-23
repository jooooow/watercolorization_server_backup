#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import datetime
import random
import os
import re
import glob
import time
import base64
import random
import threading
import subprocess
from flask import Flask, render_template
from flask import request, jsonify, send_file
from flask_socketio import SocketIO, emit

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

socketio = SocketIO()
socketio.init_app(app, cors_allowed_origins='*')
name_space = '/dcenter'

def popen_and_call(on_exit, exit_args, on_err, err_args, popen_args):
    def run_in_thread(on_exit, exit_args, on_err, err_args, popen_args):
        proc = subprocess.Popen(*popen_args, shell=True)
        proc.wait()
        returncode = proc.returncode
        if returncode == 0:
            on_exit(*exit_args)
        else:
            on_err(*err_args)
        return
    thread = threading.Thread(target=run_in_thread, args=(on_exit, exit_args, on_err, err_args, popen_args))
    thread.start()
    return thread

def watercolorization(sid):
    print("ok", sid)
    file_name_list = os.listdir("outputs")
    for file_name in file_name_list:
        if sid in file_name:
            file_path = "./outputs/" + file_name
            print(file_path)
            with open(file_path, 'rb') as f:
                image_data = f.read()
                print(len(image_data))
                socketio.emit('recv_img', {'image_data': image_data}, room=sid, namespace=name_space)
            return

def close_socket(sid):
    socketio.emit('error', "close", room=sid, namespace=name_space)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    uid = request.form['uid']
    file = request.files['img_file']
    img_name = file.filename[:file.filename.find(".")]
    img_type = file.filename[file.filename.find("."):]
    path = UPLOAD_FOLDER + "/" + img_name + "_" + uid + img_type
    print("path=",path)
    file.save(path)
    cmd = "/home/jiamian/watercolorization_v4_newgraph/gpu/build/watercolorization4_gpu --img_path=" + path + " --max_pixel_len=170 --phase_size=4 --SAVE_ROOT=./static/outputs/" + img_name + "_" + uid + "_"
    print(f"run shell on thread={threading.current_thread()}")
    with open("./std/stdout_" + uid + ".txt","wb") as out, open("./std/stderr_" + uid + ".txt","wb") as err:
        proc = subprocess.Popen(cmd,stdout=out,stderr=err,shell=True)
        proc.wait()
        returncode = proc.returncode
        print(f"run shell over, returncode={returncode}")
        if returncode == 0:
            return "200"
        else:
            return "503"
    return "500"

@app.route('/download', methods=['POST'])
def download():
    uid = request.json['uid']
    file_name_list = os.listdir("outputs")
    for file_name in file_name_list:
        if uid in file_name:
            file_path = "./outputs/" + file_name
            print(f"find file : {file_path}")
            '''with open(file_path, 'rb') as f:
                image_data = base64.b64encode(f.read())
                data = jsonify(name=file_path, data=image_data)
                return data'''
            return send_file(file_path)
    return "404"

@socketio.on('connect', namespace=name_space)
def connected_msg():
    sid = request.sid
    print(f'client connected to {sid}')
    event_name = 'onconnected'
    data = {'sid': sid}
    socketio.emit(event_name, data, room=sid, namespace=name_space)

@socketio.on('disconnect', namespace=name_space)
def disconnect_msg():
    sid = request.sid
    print(f'client disconnected from {sid}')

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=1234)
    socketio.run(app,host='0.0.0.0', port=1234)