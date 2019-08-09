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
        "apikey": os.environ.get("WML_APIKEY"),
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
    image_data = score_data[image_id]

    # トークン取得
    apikey = wml_credentials["apikey"]
    # Get an IAM token from IBM Cloud
    url     = "https://iam.bluemix.net/oidc/token"
    headers = { "Content-Type" : "application/x-www-form-urlencoded" }
    data    = "apikey=" + apikey + "&grant_type=urn:ibm:params:oauth:grant-type:apikey"
    IBM_cloud_IAM_uid = "bx"
    IBM_cloud_IAM_pwd = "bx"
    response  = requests.post( url, headers=headers, data=data, 
        auth=( IBM_cloud_IAM_uid, IBM_cloud_IAM_pwd ) )
    iam_token = response.json()["access_token"]
    print('iam_token = ', iam_token)
    
    # API呼出し用ヘッダ
    ml_instance_id = wml_credentials["instance_id"]
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + iam_token, 
      'ML-Instance-ID': ml_instance_id}

    # Webサービスの呼出し
    payload_scoring = {"values": [list(image_data)]}
    print(payload_scoring)
    scoring_response = requests.post(scoring_url, json=payload_scoring, headers=header)
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
