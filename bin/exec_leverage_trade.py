# ################################
# 取引所：GMOコイン
# 処理名：ビットコイン レバレッジ取引実行
# 作成日：2020/04/30
# ################################

import sys
import os
import click
import logging

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
    logger.setLevel(logging.DEBUG)
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
            sql = "SELECT avg(ask) as ask, avg(bid) as bid, avg(last) as last FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 5 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid, avg(last) as last FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 10 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid, avg(last) as last FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 15 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid, avg(last) as last FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 30 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid, avg(last) as last FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 60 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid, avg(last) as last FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 120 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid, avg(last) as last FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 720 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid, avg(last) as last FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 1440 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid, avg(last) as last FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 2880 MINUTE"

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
            logger.info("Start: UP/DOWN judgement.")
            ask_dict = {
                '5m': float(res[0][0]) - latest_ask,
                '10m': float(res[1][0]) - latest_ask,
                '15m': float(res[2][0]) - latest_ask,
                '30m': float(res[3][0]) - latest_ask,
                '60m': float(res[4][0]) - latest_ask,
                '120m': float(res[5][0]) - latest_ask,
                '720m': float(res[6][0]) - latest_ask,
                '1440m': float(res[7][0]) - latest_ask,
                '2880m': float(res[8][0]) - latest_ask
            }
            bid_dict = {
                '5m': float(res[0][1]) - latest_bid,
                '10m': float(res[1][1]) - latest_bid,
                '15m': float(res[2][1]) - latest_bid,
                '30m': float(res[3][1]) - latest_bid,
                '60m': float(res[4][1]) - latest_bid,
                '120m': float(res[5][1]) - latest_bid,
                '720m': float(res[6][1]) - latest_bid,
                '1440m': float(res[7][1]) - latest_bid,
                '2880m': float(res[8][1]) - latest_bid
            }
            last_dict = {
                '5m': float(res[0][2]) - latest_last,
                '10m': float(res[1][2]) - latest_last,
                '15m': float(res[2][2]) - latest_last,
                '30m': float(res[3][2]) - latest_last,
                '60m': float(res[4][2]) - latest_last,
                '120m': float(res[5][2]) - latest_last,
                '720m': float(res[6][2]) - latest_last,
                '1440m': float(res[7][2]) - latest_last,
                '2880m': float(res[8][2]) - latest_last
            }
            ask_judg = ask_dict['5m'] + ask_dict['10m'] + ask_dict['15m'] + \
                       ask_dict['30m'] + ask_dict['60m'] + ask_dict['120m'] + \
                       ask_dict['720m'] + ask_dict['1440m'] + ask_dict['2880m']
            bid_judg = bid_dict['5m'] + bid_dict['10m'] + bid_dict['15m'] + \
                       bid_dict['30m'] + bid_dict['60m'] + bid_dict['120m'] + \
                       bid_dict['720m'] + bid_dict['1440m'] + bid_dict['2880m']
            last_judg = last_dict['5m'] + last_dict['10m'] + last_dict['15m'] + \
                       last_dict['30m'] + last_dict['60m'] + last_dict['120m'] + \
                       last_dict['720m'] + last_dict['1440m'] + last_dict['2880m']
            logger.info("Ask judgement : " + str(ask_judg))
            logger.info("Bid judgement : " + str(bid_judg))
            logger.info("Last judgement : " + str(last_judg))
            logger.info("Last    5 minutes ago : " + str(last_dict['5m']))
            logger.info("Last   10 minutes ago : " + str(last_dict['10m']))
            logger.info("Last   15 minutes ago : " + str(last_dict['15m']))
            logger.info("Last   30 minutes ago : " + str(last_dict['30m']))
            logger.info("Last   60 minutes ago : " + str(last_dict['60m']))
            logger.info("Last  120 minutes ago : " + str(last_dict['120m']))
            logger.info("Last  720 minutes ago : " + str(last_dict['720m']))
            logger.info("Last 1440 minutes ago : " + str(last_dict['1440m']))
            logger.info("Last 2880 minutes ago : " + str(last_dict['2880m']))
            logger.info("End  : UP/DOWN judgement.")

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

            # 建玉一覧取得
            logger.info("Start: get open positions.")
            opJson = GA.openPositions(symbol)
            opNone = {}
            logger.info("End  : get open positions.")

            # 取引余力が10000以上・拘束証拠金が0・建玉がない場合はレバレッジ取引開始
            if availableAmount >= 10000 and margin == 0 and opJson['data'] == opNone:
                logger.info("Start: leverage trading.")

                logger.info("End  : leverage trading.")
        else:
            logger.warning("The exchange is not open.")

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