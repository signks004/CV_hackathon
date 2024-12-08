#!/usr/bin/env python
from importlib import import_module
import os
import sys
import datetime
import threading
from flask import Flask, render_template, Response
from pyfladesk import init_gui
from camera import Camera,resource_path
from audiopy import start_player

##C:\Program Files (x86)\Windows Kits\10\Redist\ucrt\DLLs\x64 <<-add to path when building

perfect = resource_path(os.path.join('static', 'perfect.mp3'))
icon = resource_path(os.path.join('static', 'appicon.png'))

'''tell flask where too look for resources
if this is bundled in 1 file'''
if getattr(sys, 'frozen', False):
    template_folder = resource_path('templates')
    static_folder = resource_path('static')
    app = Flask(__name__, template_folder=template_folder,
                static_folder=static_folder)
else:
    app = Flask(__name__)

# initiate the camera
webcam = Camera()

# @desc= GET '/' render the index.html

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


@app.route('/start', methods=["POST"])
def start():
    """start scoring - turn on eye classifier"""
    webcam.set_classifier(1)
    timestamp = datetime.datetime.now()
    webcam.set_time_start(timestamp)
    return "Classifier ON - Status {0}\n Time Start: {1}".format(webcam.classifier, timestamp)


@app.route('/stop', methods=["POST"])
def stop():
    """stop scoring - turn off eye classifier"""
    webcam.set_classifier(0)
    final = webcam.get_score()
    timestamp = datetime.datetime.now()
    webcam.set_time_end(timestamp)
    duration = webcam.get_duration()
    webcam.camera_reset()
    if final == 100:
        try:
            playthread = threading.Thread(target=start_player, args=(perfect,) )
            playthread.start()
        except Exception as e:
            print(e)
        

    points = duration * 10 * final/10
    print(points)
    return "Final Score: {0}\n Duration: {1} \n Total Points: {2}".format(final,duration, points)


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/restart', methods=['POST'])
def restart():
    """restarts camera"""
    webcam = Camera()
    return "Camera restarted"

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(response=gen(webcam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    init_gui(app, port=5000, width=640, height=800,
             window_title="WAKEY", icon=icon, argv=None)
