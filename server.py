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
import operator
import subprocess
from flask import Flask, render_template
from flask import request, jsonify, send_file, session
from flask_socketio import SocketIO, emit
from threading import Thread, Lock

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = "this is the key for watercolorization server"

socketio = SocketIO()
socketio.init_app(app, cors_allowed_origins='*')
name_space = '/dcenter'

lock = Lock()

gpu_flags = [0] * 5

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

@app.route('/back')
def back():
    dir = "./static/outputs"
    file_name_list = os.listdir(dir)
    file_name_list_sorted = []
    for file_name in file_name_list:
        t = datetime.datetime.fromtimestamp(os.path.getctime(dir + "/" + file_name))
        file_name_list_sorted.append([file_name, t])
    file_name_list_sorted = sorted(file_name_list_sorted, key=operator.itemgetter(1))
    file_name_list_sorted.reverse()
    html = "<body><table>"
    for file_name, t in file_name_list_sorted:
        #html += "<tr><a href='/static/outputs/" + file_name + "'><td>" + str(t) + "</td><td>" + file_name + "</td></a><tr>"
        html += "<tr><td>" + str(t) + "</td><td><a href='/static/outputs/" + file_name + "'>" + file_name + "</a></td><tr>"
    html += "</table></body>"
    return html

@app.route('/upload', methods=['POST'])
def upload():
    uid = request.form['uid']
    file = request.files['img_file']
    img_name = file.filename[:file.filename.find(".")]
    img_type = file.filename[file.filename.find("."):]
    path = UPLOAD_FOLDER + "/" + img_name + "_" + uid + img_type
    print("path=",path)
    file.save(path)
    gpu_id = -1
    lock.acquire()
    for i, flag in enumerate(gpu_flags):
        if flag == 0:
            gpu_flags[i] = 1
            gpu_id = i
            break
    lock.release()
    if gpu_id == -1:
        print("busy", uid)
        return "403"
    cmd = "/home/jiamian/watercolorization_v4_newgraph/gpu/build/watercolorization4_gpu --img_path=" + path + " --max_pixel_len=170 --phase_size=4 --gpu_id=" + str(gpu_id) + " --SAVE_ROOT=./static/outputs/" + img_name + "_" + uid + "_"
    print(f"run shell on thread={threading.current_thread()}")
    with open("./std/stdout_" + uid + ".txt","wb") as out, open("./std/stderr_" + uid + ".txt","wb") as err:
        proc = subprocess.Popen(cmd,stdout=out,stderr=err,shell=True)
        proc.wait()
        lock.acquire()
        gpu_flags[gpu_id] = 0
        lock.release()
        returncode = proc.returncode
        print(f"run shell over, returncode={returncode}")
        if returncode == 0:
            return "200"
        else:
            return "503"
    lock.acquire()
    gpu_flags[gpu_id] = 0
    lock.release()
    return "500"

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