#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import os
from flask import Flask, request, render_template
from sklearn import datasets
import numpy
from PIL import Image
import urllib3
import json
from cfenv import AppEnv
from os.path import join, dirname
from dotenv import load_dotenv

# 認証情報の読み取り (.env または IBM Cloud上のバインド)
env = AppEnv()
pm20 = env.get_service(label='pm-20')
if pm20 is None:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    wml_credentials = {
        "url": os.environ.get("WML_URL"),
        "access_key": os.environ.get("WML_ACCESS_KEY"),
        "username": os.environ.get("WML_USERNAME"),
        "password":  os.environ.get("WML_PASSWORD"),
        "instance_id": os.environ.get("WML_INSTANCE_ID")
    }
else:
    wml_credentials = pm20.credentials

# スコアリングURLの読み取り (.env または環境変数)
scoring_url = os.environ.get("SCORING_URL")

# 手書き文字データの読み込み
digits = datasets.load_digits()
samples_count = len(digits.images)
score_data = digits.data[int(0.9*samples_count): ]
score_labels = digits.target[int(0.9*samples_count): ]
score_images = digits.images[int(0.9*samples_count): ]

app = Flask(__name__)

@app.route('/')
def top():
    name = "Top"
    return render_template('wml-sample.html', title='WML Test', name=name)

# 「テスト対象選択」ボタンが押された時の処理
@app.route('/select_image', methods=['GET'])
def select_image():
    print('/select_image')
    image_id = int(request.args.get('image_id', ''))
    image = score_images[image_id]
    label = score_labels[image_id]
    pilImg = Image.fromarray(numpy.uint8((16 - image) * 15))
    pilImg.save('static/image.png')
    return str(label)

# 「予測」ボタンが押された時の処理
@app.route('/predict', methods=['GET'])
def predict():
    print('/predict')
    image_id = int(request.args.get('image_id', ''))
    data = score_data[image_id]

    # Basic認証用ヘッダの生成
    auth = '{username}:{password}'.format(username=wml_credentials['username'], password=wml_credentials['password'])
    header_basic_auth = urllib3.util.make_headers(basic_auth=auth)
    url = '{}/v3/identity/token'.format(wml_credentials['url'])

    # Tokenの取得
    mltoken =  json.loads( requests.get(url, headers=header_basic_auth).text )['token']
    print(mltoken)
    header_token = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

    # Webサービスの呼出し
    payload_scoring = {"values": [list(data)]}
    print(payload_scoring)
    scoring_response = requests.post(scoring_url, json=payload_scoring, headers=header_token)
    scoring = json.loads( scoring_response.text )

    # 結果の取得
    predict_list = [item[0] for item in scoring['values']]
    predict_str = str(predict_list[0])
    print(predict_str)
    return predict_str

@app.route('/favicon.ico')
def favicon():
   return ""

port = os.getenv('VCAP_APP_PORT', '8000')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(port), debug=True)
