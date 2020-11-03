# ################################
# 取引所：GMOコイン
# 処理名：取引所情報取得
# 作成日：2020/04/30
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
from conf.config import EndpointConf as EC

class GmoApi(object):
    # 取引所ステータス取得
    def exStatus():
        path = '/v1/status'
        response = requests.get(EC.pubUrl + path)
        data = response.json()
        if int(data['status']) == 0:
            status = data['data']['status']
        else:
            status = data['messages'][0]['message_string']
        return status

    # 最新レート取得
    def latestRate(symbol):
        path = '/v1/ticker?symbol=' + symbol
        response = requests.get(EC.pubUrl + path)
        data = response.json()
        return data

    # 板情報取得
    def orderbooks(symbol):
        path = '/v1/orderbooks?symbol=' + symbol
        response = requests.get(EC.pubUrl + path)
        data = response.json()
        return data

    # 余力情報取得
    def availableAmount():
        endPoint  = EC.priUrl
        apiKey    = EC.apiKey
        secretKey = EC.secretKey
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        method = 'GET'
        path = '/v1/account/margin'
        text = timestamp + method + path
        sign = hmac.new(bytes(secretKey.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

        headers = {
            "API-KEY": apiKey,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }
        response = requests.get(endPoint + path, headers=headers)
        data = response.json()
        return data

    # 建玉一覧取得
    def openPositions(symbol):
        endPoint  = EC.priUrl
        apiKey    = EC.apiKey
        secretKey = EC.secretKey
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        method = 'GET'
        path = '/v1/openPositions'
        text = timestamp + method + path
        sign = hmac.new(bytes(secretKey.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

        parameters = {
            "symbol": symbol,
            "page": 1,
            "count": 100
        }
        headers = {
            "API-KEY": apiKey,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }
        response = requests.get(endPoint + path, headers=headers, params=parameters)
        data = response.json()
        return data

    # 建玉サマリー取得
    def positionSummary(symbol):
        endPoint  = EC.priUrl
        apiKey    = EC.apiKey
        secretKey = EC.secretKey
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        method = 'GET'
        path = '/v1/positionSummary'
        text = timestamp + method + path
        sign = hmac.new(bytes(secretKey.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

        parameters = {
            "symbol": symbol
        }
        headers = {
            "API-KEY": apiKey,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }
        response = requests.get(endPoint + path, headers=headers, params=parameters)
        data = response.json()
        return data

    # 有効注文一覧取得
    def activeOrders(symbol):
        endPoint  = EC.priUrl
        apiKey    = EC.apiKey
        secretKey = EC.secretKey
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        method = 'GET'
        path = '/v1/activeOrders'
        text = timestamp + method + path
        sign = hmac.new(bytes(secretKey.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

        parameters = {
            "symbol": symbol,
            "page": 1,
            "count": 100
        }
        headers = {
            "API-KEY": apiKey,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }
        response = requests.get(endPoint + path, headers=headers, params=parameters)
        data = response.json()
        return data

    # 成行注文
    def openOrder(symbol, side, size):
        endPoint  = EC.priUrl
        apiKey    = EC.apiKey
        secretKey = EC.secretKey
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        method    = 'POST'
        path      = '/v1/order'
        reqBody = {
            "symbol": symbol,
            "side": side,
            "executionType": "MARKET",
            "size": size
        }

        text = timestamp + method + path + json.dumps(reqBody)
        sign = hmac.new(bytes(secretKey.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

        headers = {
            "API-KEY": apiKey,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }

        response = requests.post(endPoint + path, headers=headers, data=json.dumps(reqBody))
        data = response.json()
        return data

    # 決済注文
    def closeOrder(symbol, side, price, positionId, size, executionType):
        endPoint  = EC.priUrl
        apiKey    = EC.apiKey
        secretKey = EC.secretKey
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        method    = 'POST'
        path      = '/v1/closeOrder'
        reqBody = {
            "symbol": symbol,
            "side": side,
            "executionType": executionType,
            "price": price,
            "settlePosition": [
                {
                    "positionId": positionId,
                    "size": size
                }
            ]
        }

        text = timestamp + method + path + json.dumps(reqBody)
        sign = hmac.new(bytes(secretKey.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

        headers = {
            "API-KEY": apiKey,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }

        response = requests.post(endPoint + path, headers=headers, data=json.dumps(reqBody))
        data = response.json()
        return data

    # 一括決済注文
    def closeBulkOrder(symbol, side, price, size, executionType):
        endPoint  = EC.priUrl
        apiKey    = EC.apiKey
        secretKey = EC.secretKey
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        method    = 'POST'
        path      = '/v1/closeBulkOrder'
        reqBody = {
            "symbol": symbol,
            "side": side,
            "executionType": executionType,
            "price": price,
            "size": size
        }

        text = timestamp + method + path + json.dumps(reqBody)
        sign = hmac.new(bytes(secretKey.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

        headers = {
            "API-KEY": apiKey,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }

        response = requests.post(endPoint + path, headers=headers, data=json.dumps(reqBody))
        data = response.json()
        return data

    # 一括決済注文
    def closeBulkOrderMarket(symbol, side, size, executionType):
        endPoint  = EC.priUrl
        apiKey    = EC.apiKey
        secretKey = EC.secretKey
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        method    = 'POST'
        path      = '/v1/closeBulkOrder'
        reqBody = {
            "symbol": symbol,
            "side": side,
            "executionType": executionType,
            "size": size
        }

        text = timestamp + method + path + json.dumps(reqBody)
        sign = hmac.new(bytes(secretKey.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

        headers = {
            "API-KEY": apiKey,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }

        response = requests.post(endPoint + path, headers=headers, data=json.dumps(reqBody))
        data = response.json()
        return data

    # ロスカットレート変更
    def changeLosscutPrice(positionId, losscutPrice):
        endPoint  = EC.priUrl
        apiKey    = EC.apiKey
        secretKey = EC.secretKey
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        method    = 'POST'
        path      = '/v1/changeLosscutPrice'
        reqBody = {
            "positionId": positionId,
            "losscutPrice": losscutPrice
        }

        text = timestamp + method + path + json.dumps(reqBody)
        sign = hmac.new(bytes(secretKey.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

        headers = {
            "API-KEY": apiKey,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }

        response = requests.post(endPoint + path, headers=headers, data=json.dumps(reqBody))
        data = response.json()
        return data

    # 注文キャンセル
    def cancelOrder(orderId):
        endPoint  = EC.priUrl
        apiKey    = EC.apiKey
        secretKey = EC.secretKey
        timestamp = '{0}000'.format(int(time.mktime(datetime.now().timetuple())))
        method    = 'POST'
        path      = '/v1/cancelOrder'
        reqBody = {
            "orderId": orderId
        }

        text = timestamp + method + path + json.dumps(reqBody)
        sign = hmac.new(bytes(secretKey.encode('ascii')), bytes(text.encode('ascii')), hashlib.sha256).hexdigest()

        headers = {
            "API-KEY": apiKey,
            "API-TIMESTAMP": timestamp,
            "API-SIGN": sign
        }

        response = requests.post(endPoint + path, headers=headers, data=json.dumps(reqBody))
        data = response.json()
        return data