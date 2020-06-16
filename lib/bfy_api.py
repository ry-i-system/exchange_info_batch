# ################################
# 取引所：bitFlyer
# 処理名：取引所情報取得
# 作成日：2020/06/16
# ################################

import sys
import os
import requests
import json
import hmac
import hashlib
import time
from datetime import datetime

# 親ディレクトリをアプリケーションのホーム(${app_home})に設定
app_home = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)) , ".." ))
# ${app_home}をライブラリロードパスに追加
sys.path.append(os.path.join(app_home))

# 設定クラスのロード
from conf.config import BitFlyerConf as EC

class BfyApi(object):
    # 取引所ステータス取得
    def exStatus():
        path = '/v1/gethealth'
        response = requests.get(EC.pubUrl + path)
        data = response.json()
        status = data['status']
        return status

    # 最新レート取得
    def latestRate(symbol):
        path = '/v1/ticker?product_code=' + symbol
        response = requests.get(EC.pubUrl + path)
        data = response.json()
        return data
