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
from flask import Flask, render_template,make_response
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
        html += "<tr><td>" + str(t) + "</td><td><a href='/static/outputs/" + file_name + "'>" + file_name + "</a></td><tr>"
    html += "</table></body>"
    return html

@app.route('/upload', methods=['POST'])
def upload():
    try:
        uid = request.form['uid']
        file = request.files['img_file']
        scale = request.form['scale']
        layers = request.form['layers']
        ETF = request.form['ETF']
        print(f'uid={uid}, file={file}, scale={scale}, layers={layers}, ETF={ETF}')
        img_name = file.filename[:file.filename.find(".")]
        img_type = file.filename[file.filename.find("."):]
        img_path = UPLOAD_FOLDER + "/" + img_name + "@" + uid + img_type
        out_path = "./static/outputs/" + img_name + "@" + uid + "@"
        print("img_path=",img_path)
        file.save(img_path)
    except Exception as e:
        return {"status":"request error"}

    gpu_id = -1
    lock.acquire()
    for i, flag in enumerate(gpu_flags):
        if flag == 0:
            gpu_flags[i] = 1
            gpu_id = i
            break
    lock.release()
    if gpu_id == -1:
        return {"status":"busy"}
        
    socketio.emit("process_begin", room=uid, namespace=name_space)

    try:
        cmd = "/home/jiamian/watercolorization_v4_newgraph/gpu/build/watercolorization4_gpu" \
            + " --img_path=" + img_path \
            + " --max_pixel_len=170 --default_phase_size=4 --gpu_id=" + str(gpu_id) \
            + " --SAVE_ROOT=" + out_path \
            + " --src_scale=" + scale \
            + " --layer_size=" + layers \
            + " --ETF=" + ETF 

        start = time.time()
        proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL, shell=True)
        stdout, _ = proc.communicate()
        total_process_time = re.findall(r'total time measured : (.+?) seconds', str(stdout))
        total_process_time = "?" if len(total_process_time) == 0 else total_process_time[0]
        compute_time = re.findall(r'compute time measured : (.+?) seconds', str(stdout))
        compute_time = "?" if len(compute_time) == 0 else compute_time[0]
        end = time.time()
        img_size = re.findall(r'img_size\[(\d+) \* (\d+)\]', str(stdout))
        img_size = ("?","?") if len(img_size) == 0 else str(img_size[0][0]),str(img_size[0][1])
        if proc.returncode == 0:
            with open("./std/stdout_" + uid + ".txt","wb") as out:
                out.write(stdout)
            old_output_img_path = out_path + "result.png"
            new_output_img_path = out_path \
                                + "size" + img_size[0] + "x" + img_size[1] + "@" \
                                + "scale" + str(scale) + "@" \
                                + "layers" + str(layers) + "@" \
                                + "ETF" + str(ETF) + "@" \
                                + "totaltime" + str(total_process_time) + "@" \
                                + "computetime" + str(compute_time) + "@" \
                                + "result.png"
            os.rename(old_output_img_path , new_output_img_path)
        
            lock.acquire()
            gpu_flags[gpu_id] = 0
            lock.release()
            return {"status":"200", "total_process_time":total_process_time, "compute_time":compute_time, "output_img_path":new_output_img_path}
    except Exception as e:
        lock.acquire()
        gpu_flags[gpu_id] = 0
        lock.release()
        return {"status":"cmd error, " + str(e)}

    lock.acquire()
    gpu_flags[gpu_id] = 0
    lock.release()

    return {"status":"exec_error(try to change the scale)"}

@app.route('/download', methods=['GET'])
def download():
    #with open("./static/img/hiroshima-university.png", 'r') as img:
    return send_file("./static/img/hiroshima-university.png", mimetype='image/png')

@socketio.on('connect', namespace=name_space)
def connected_msg():
    sid = request.sid
    print(f'connected with {sid}')
    event_name = 'onconnected'
    data = {'sid': sid}
    socketio.emit(event_name, data, room=sid, namespace=name_space)

@socketio.on('disconnect', namespace=name_space)
def disconnect_msg():
    sid = request.sid
    print(f'disconnected with {sid}')


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=1234)
    socketio.run(app,host='0.0.0.0', port=1234)