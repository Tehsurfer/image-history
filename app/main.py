import json
import base64

import requests

from flask import Flask, abort, jsonify, request
from flask_cors import CORS

from app.config import Config


import os
import schedule
import threading
import time
from pathlib import Path

app = Flask(__name__)
# set environment variable
app.config["ENV"] = Config.DEPLOY_ENV

CORS(app)
times = []
image_count = 0
image_path = Path('images')


def schedule_check():
    while True:
        schedule.run_pending()
        time.sleep(5)


def image_run():
    try:
        update_images()
    except Exception as e:
        print('hit exepction!')
        print(e)
        pass

def get_image():
    r = requests.get('http://www.windsurf.co.nz/webcams/takapuna.jpg')
    if r.status_code is 200:
        return r.content
    else:
        print(r.status_code)
        print(r.text)

def save_image(image, filename):
    f = open(image_path / filename, 'wb')  # first argument is the filename
    f.write(image)
    f.close()

def create_filename():
    global image_count
    name = f'takapuna{image_count}.png'
    image_count += 1
    return name

def cleanup_database():
    for name in os.listdir('images'):
        if name == f'takapuna{image_count-20}.png':
            os.remove(image_path / name)

def update_images():
    image = get_image()
    name = create_filename()
    save_image(image, name)
    cleanup_database()


schedule.every(5).minutes.do(image_run)
x = threading.Thread(target=schedule_check, daemon=True)
x.start()

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.route("/health")
def health():
    return json.dumps({"status": "healthy"})

@app.route("/")
def cam():
    return create_page_from_images( get_latest_images() )

def get_latest_images():
    global image_count
    i = image_count - 40
    if i < 0:
        i = 0
    image_list = []
    while i <= image_count:
        data_uri = base64.b64encode(open( image_path / f'takapuna{i}.png', 'rb').read()).decode('utf-8')
        img_tag = '<img src="data:image/png;base64,{0}">'.format(data_uri)
        image_list.append(img_tag)
        i += 1
    return image_list

def create_page_from_images(image_list):
    page = ''
    for im in image_list:
        page += im
        page += '\n'
    return page
