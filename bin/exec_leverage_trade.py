# ################################
# 取引所：GMOコイン
# 処理名：ビットコイン レバレッジ取引実行
# 作成日：2020/04/30
# ################################

import sys
import os
import click
import logging
import time
import math

# 親ディレクトリをアプリケーションのホーム(${app_home})に設定
app_home = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)) , ".." ))
# ${app_home}をライブラリロードパスに追加
sys.path.append(os.path.join(app_home))

# 自前のライブラリをロード
from lib.db_access import DbAccess as DA
from lib.gmo_api import GmoApi as GA

# コマンドライン引数のハンドリング. must_argは必須オプション、optional_argは任意オプション
@click.command()
@click.option('--ex_cd', '-e', required=True)
@click.option('--symbol','-s', required=True)
def execLeveregeTrade(ex_cd,symbol):
    # 自身の名前から拡張子を除いてプログラム名(${prog_name})にする
    prog_name = os.path.splitext(os.path.basename(__file__))[0]

    # ロガーの設定

    # フォーマット
    log_format = logging.Formatter("%(asctime)s [%(levelname)8s] %(message)s")
    # レベル
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    # 標準出力へのハンドラ
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(log_format)
    logger.addHandler(stdout_handler)
    # ログファイルへのハンドラ
    file_handler = logging.FileHandler(os.path.join(app_home,"log", prog_name + ".log"), "a+")
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    # 処理開始
    try:
        # ログ出力
        logger.info("----- start -----")

        # コマンドライン引数の利用
        logger.info(f"ex_cd = {ex_cd}")
        logger.info(f"symbol = {symbol}")

        # 取引所ステータス取得
        status = GA.exStatus()

        # 取引所がOPENの場合
        if status == "OPEN":
            logger.info("The exchange is open.")

            # 登録データ定義
            ex_cd = f"{ex_cd}"
            symbol = f"{symbol}"

            # DB接続
            logger.info("Start: DB connection.")
            # 過去データ取得SQL
            sql = "SELECT avg(ask) as ask, avg(bid) as bid, avg(last) as last FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 1 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid, avg(last) as last FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 5 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid, avg(last) as last FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 10 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid, avg(last) as last FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 15 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid, avg(last) as last FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 30 MINUTE"

            res = DA.dbSelect(sql)
            logger.info("End  : DB connection.")

            # 最新レート取得
            logger.info("Start: get the latest rate.")
            latestRateJson = GA.latestRate(symbol)
            # 最新Ask
            latest_ask = float(latestRateJson['data'][0]['ask'])
            # 最新Bid
            latest_bid = float(latestRateJson['data'][0]['bid'])
            # 最新Last
            latest_last = float(latestRateJson['data'][0]['last'])
            # 最新スプレッド
            latest_spread = latest_ask - latest_bid
            logger.info("End  : get the latest rate.")

            # UP/DOWN判定
            logger.info("Start: UP/DOWN judgment.")
            last_dict = {
                '1m': float(res[0][2]) - latest_last,
                '5m': float(res[1][2]) - latest_last,
                '10m': float(res[2][2]) - latest_last,
                '15m': float(res[3][2]) - latest_last,
                '30m': float(res[4][2]) - latest_last
            }
            last_ud = {
                '1m': -1 if last_dict['1m'] > 0 else 1 if last_dict['1m'] < 0 else 0,
                '5m': -1 if last_dict['5m'] > 0 else 1 if last_dict['5m'] < 0 else 0,
                '10m': -1 if last_dict['10m'] > 0 else 1 if last_dict['10m'] < 0 else 0,
                '15m': -1 if last_dict['15m'] > 0 else 1 if last_dict['15m'] < 0 else 0,
                '30m': -1 if last_dict['30m'] > 0 else 1 if last_dict['30m'] < 0 else 0
            }
            last_judg = last_ud['1m'] + last_ud['5m'] + last_ud['10m'] + last_ud['15m'] + last_ud['30m']
            logger.info("Last judgment : " + str(last_judg))
            logger.info("Last    1 minutes ago : " + str(last_ud['1m']))
            logger.info("Last    5 minutes ago : " + str(last_ud['5m']))
            logger.info("Last   10 minutes ago : " + str(last_ud['10m']))
            logger.info("Last   15 minutes ago : " + str(last_ud['15m']))
            logger.info("Last   30 minutes ago : " + str(last_ud['30m']))
            logger.info("End  : UP/DOWN judgment.")

            # 拘束証拠金取得
            logger.info("Start: get available amount.")
            aaJson = GA.availableAmount()
            availableAmount = int(aaJson['data']['availableAmount'])
            margin = int(aaJson['data']['margin'])
            logger.info("ActualProfitLoss : " + str(aaJson['data']['actualProfitLoss']))
            logger.info("AvailableAmount  : " + str(aaJson['data']['availableAmount']))
            logger.info("Margin           : " + str(aaJson['data']['margin']))
            logger.info("ProfitLoss       : " + str(aaJson['data']['profitLoss']))
            logger.info("End  : get available amount.")

            time.sleep(1)

            # 建玉一覧取得
            logger.info("Start: get open positions.")
            opJson = GA.openPositions(symbol)
            opNone = {}
            logger.info("End  : get open positions.")

            time.sleep(1)

            # 有効注文一覧取得
            logger.info("Start: get active orders.")
            apJson = GA.activeOrders(symbol)
            apNone = {}
            logger.info("End  : get active orders.")

            time.sleep(1)

            # 取引設定取得
            logger.info("Start: DB connection.")
            res = DA.dbSelect("SELECT * FROM eip_trade_config")
            # 取引コインサイズ
            coin_size = float(res[0][2])
            # 取引スプレッド
            spread = int(res[0][3])
            # 取引範囲
            price_range = int(res[0][4])
            # 余力下限
            available_amount = int(res[0][5])
            # ロスカット指数
            losscut_index = int(res[0][6])
            logger.info("End  : DB connection.")

            # 建玉がなければ正
            if opJson['data'] == opNone:
                # 拘束証拠金が0であれば正
                if margin == 0:
                    # 余力が10000以上であれば正
                    if availableAmount >= available_amount:
                        # 最新レートのスプレッドが設定値以内であれば正
                        if latest_spread >= -spread and latest_spread <= spread:
                            # レバレッジ取引開始
                            logger.info("Start: leverage trade.")
                            # 上昇予想の場合
                            if last_judg > 0:
                                # 買い成行注文
                                logger.info("It is expected to rise.")
                                logger.info("Start: Buy order.")
                                ooJson = GA.openOrder(symbol, "BUY", coin_size)
                                logger.info("End  : Buy order.")

                                # 建玉取得
                                logger.info("Start: get open positions.")
                                opJson = GA.openPositions(symbol)
                                # positionId = opJson['data']['list'][0]['positionId']
                                price = int(opJson['data']['list'][0]['price']) + price_range
                                # losscutPrice = math.ceil(int(opJson['data']['list'][0]['price']) - ((int(opJson['data']['list'][0]['price']) / 4) /2))
                                # stop_price = int(opJson['data']['list'][0]['price']) - (price_range * losscut_index)
                                logger.info("End  : get open positions.")

                                time.sleep(1)

                                # 売り指値決済注文
                                logger.info("Start: Sell close order.")
                                coJson = GA.closeBulkOrder(symbol, "SELL", price, coin_size, "LIMIT")
                                logger.info("End  : Sell close order.")

                                # time.sleep(1)

                                # ロスカットレート変更
                                # logger.info("Start: Change losscut price.")
                                # coJson = GA.closeBulkOrder(positionId, losscutPrice)
                                # logger.info("End  : Change losscut price.")

                            # 下降予想の場合
                            elif last_judg < 0:
                                # 売り成行注文
                                logger.info("It is expected to decline.")
                                logger.info("Start: Sell order.")
                                ooJson = GA.openOrder(symbol, "SELL", coin_size)
                                logger.info("End  : Sell order.")

                                # 建玉取得
                                logger.info("Start: get open positions.")
                                opJson = GA.openPositions(symbol)
                                # positionId = opJson['data']['list'][0]['positionId']
                                price = int(opJson['data']['list'][0]['price']) - price_range
                                # losscutPrice = math.ceil(int(opJson['data']['list'][0]['price']) + ((int(opJson['data']['list'][0]['price']) / 4) /2))
                                # stop_price = int(opJson['data']['list'][0]['price']) + (price_range * losscut_index)
                                logger.info("End  : get open positions.")

                                time.sleep(1)

                                # 買い指値決済注文
                                logger.info("Start: Buy close order.")
                                coJson = GA.closeBulkOrder(symbol, "BUY", price, coin_size, "LIMIT")
                                logger.info("End  : Buy close order.")

                                # time.sleep(1)

                                # ロスカットレート変更
                                # logger.info("Start: Change losscut price.")
                                # coJson = GA.closeBulkOrder(positionId, losscutPrice)
                                # logger.info("End  : Change losscut price.")

                            else:
                                # 予想できない場合は取引しない
                                logger.info("Unexpected because the judgment index is 0.")
                            # レバレッジ取引終了
                            logger.info("End  : leverage trade.")
                        else:
                            # スプレッドが広いため取引しない
                            logger.info("The spread is not within -" + str(spread) + " ~ " + str(spread) + ".")
                    else:
                        # 余力が10000以下の場合、取引しない
                        logger.info("Trading capacity (availableAmount) is below " + str(available_amount) + ".")
                else:
                    # 拘束証拠金が0出ない場合、取引しない
                    logger.info("Detention margin is not 0.")
            else:
                # 決済注文がなければ入れる
                if apJson['data'] == apNone:
                    # 上昇予想の場合
                    if last_judg > 0:
                        # 建玉取得
                        # positionId = opJson['data']['list'][0]['positionId']
                        price = int(opJson['data']['list'][0]['price']) + price_range
                        # losscutPrice = math.ceil(int(opJson['data']['list'][0]['price']) - ((int(opJson['data']['list'][0]['price']) / 4) /2))
                        # stop_price = int(opJson['data']['list'][0]['price']) - (price_range * losscut_index)

                        time.sleep(1)

                        # 売り指値決済注文
                        logger.info("Start: Sell close order.")
                        coJson = GA.closeBulkOrder(symbol, "SELL", price, coin_size, "LIMIT")
                        logger.info("End  : Sell close order.")

                        # time.sleep(1)

                        # ロスカットレート変更
                        # logger.info("Start: Change losscut price.")
                        # coJson = GA.closeBulkOrder(positionId, losscutPrice)
                        # logger.info("End  : Change losscut price.")
                    # 下降予想の場合
                    elif last_judg < 0:
                        # positionId = opJson['data']['list'][0]['positionId']
                        price = int(opJson['data']['list'][0]['price']) - price_range
                        # losscutPrice = math.ceil(int(opJson['data']['list'][0]['price']) + ((int(opJson['data']['list'][0]['price']) / 4) /2))
                        # stop_price = int(opJson['data']['list'][0]['price']) + (price_range * losscut_index)

                        time.sleep(1)

                        # 買い指値決済注文
                        logger.info("Start: Buy close order.")
                        coJson = GA.closeBulkOrder(symbol, "BUY", price, coin_size, "LIMIT")
                        logger.info("End  : Buy close order.")

                        # time.sleep(1)

                        # ロスカットレート変更
                        # logger.info("Start: Change losscut price.")
                        # coJson = GA.closeBulkOrder(positionId, losscutPrice)
                        # logger.info("End  : Change losscut price.")
                else:
                    # 現在の評価損益を取得
                    psJson = GA.positionSummary(symbol)
                    lossGain = int(psJson['data']['list'][0]['positionLossGain'])
                    side = psJson['data']['list'][0]['side']
                    coin_size = psJson['data']['list'][0]['sumPositionQuantity']

                    # 損失が大きい場合は注文キャンセル
                    if lossGain < (price_range / 4) * -1:
                        logger.info("Start: Cancel order.")
                        for i in apJson['data']['list']:
                            GA.cancelOrder(i['orderId'])
                            time.sleep(1)
                        logger.info("End  : Cancel order.")
                    
                        # 成行で一括決済注文
                        if side == "BUY":
                            orderSide = "SELL"
                        else:
                            orderSide = "BUY"
                        logger.info("Start: close order.")
                        coJson = GA.closeBulkOrderMarket(symbol, orderSide, coin_size, "MARKET")
                        logger.info("End  : close order.")
        else:
            # 取引所がOPENでない
            logger.info("The exchange is not open.")

        # 処理終了
        logger.info("End processing.")
        # ログ出力
        logger.info("----- end -----")
        sys.exit(0)

    except Exception as e:
        # キャッチして例外をログに記録
        logger.exception(e)
        # ログ出力
        logger.error("----- end -----")
        sys.exit(1)

if __name__ == '__main__':
    execLeveregeTrade()