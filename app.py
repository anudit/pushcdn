from pushbullet import PushBullet
import json
import os
from dotenv import load_dotenv
from flask import Flask
import requests
from flask import Flask, request, render_template, Response
from werkzeug import secure_filename

app = Flask(__name__)
load_dotenv()

APIKEY = os.environ.get("APIKEY")
CHANNEL = os.environ.get("CHANNEL")
print(CHANNEL)
p = PushBullet(APIKEY)

def getPushUrl(file_address = None):
    if (os.path.isfile(file_address) == False):
        raise ValueError("invalid path")

    activeSubs = p.active(p.getSubscriptions())
    checkCDN = [x for x in activeSubs if (x['channel']['tag'] == CHANNEL)]
    channelID = checkCDN[0]['channel']['iden']
    if (checkCDN):
        p.pushFile(CHANNEL, os.path.basename(file_address), os.path.splitext(file_address)[0], open(file_address, "rb"), recipient_type = "channel_tag")
        chats = p.getPushHistory();
        for x in chats:
            if ('channel_iden' in x and 'file_url' in x):
                    if (x['channel_iden'] == channelID):
                        return x['file_url']
    else:
        raise Exception("No Channel Setup")

@app.route('/')
def start():
    return "Hello"

@app.route('/test')
def test():
    link = getPushUrl("link.png")
    return link

@app.route('/uploader', methods = ['POST'])
def upload_file():
    print(request.files)
    f = request.files['file']
    print(f)
    name  = str(int(time.time()))
    ext = str(f.filename).split(".")[-1]
    path = os.path.join(os.environ.get['UPLOAD_FOLDER'], secure_filename(name)+"."+ext)
    f.save(path)
    url = getPushUrl(path)
    print(url)
    data = {
        'url'  : url,
    }
    js = json.dumps(data)

    resp = Response(js, status=200, mimetype='application/json')
    return resp

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)