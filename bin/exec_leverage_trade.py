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
@click.option('--must_arg', '-f', required=True)
@click.option('--optional_arg','-o',default="BTC_JPY")
def gmoGetLatestRate(must_arg,optional_arg):
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
        logger.info(f"must_arg = {must_arg}")
        logger.info(f"optional_arg = {optional_arg}")

        # 取引所ステータス取得
        status = GA.exStatus()

        # 取引所がOPENの場合
        if status == "OPEN":
            logger.info("The exchange is open.")

            # 登録データ定義
            ex_cd = f"{must_arg}"
            symbol = f"{optional_arg}"

            # DB接続
            logger.info("Start: DB connection.")
            # 過去データ取得SQL
            sql = "SELECT avg(ask) as ask, avg(bid) as bid FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 5 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 10 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 15 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 30 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 60 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 120 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 720 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 1440 MINUTE \
                   UNION ALL \
                   SELECT avg(ask) as ask, avg(bid) as bid FROM eip_latest_rate WHERE datetime > CURRENT_TIMESTAMP + INTERVAL - 2880 MINUTE"

            res = DA.dbSelect(sql)
            logger.info("End  : DB connection.")

            # 最新レート取得
            logger.info("Start: get the latest rate.")
            latestRateJson = GA.latestRate(symbol)
            # 最新ASK
            latest_ask = float(latestRateJson['data'][0]['ask'])
            # 最新BID
            latest_bid = float(latestRateJson['data'][0]['bid'])
            # 最新スプレッド
            latest_spread = latest_ask - latest_bid
            logger.info("End  : get the latest rate.")

            # UP/DOWN判定
            logger.info("Start: UP/DOWN judgement.")
            ask_dict = {
                '5m': float(res[0][0]) - latest_ask,
                '10m': float(res[0][0]) - latest_ask,
                '15m': float(res[0][0]) - latest_ask,
                '30m': float(res[0][0]) - latest_ask,
                '60m': float(res[0][0]) - latest_ask,
                '120m': float(res[0][0]) - latest_ask,
                '720m': float(res[0][0]) - latest_ask,
                '1440m': float(res[0][0]) - latest_ask,
                '2880m': float(res[0][0]) - latest_ask
            }
            bid_dict = {
                '5m': float(res[0][0]) - latest_bid,
                '10m': float(res[0][0]) - latest_bid,
                '15m': float(res[0][0]) - latest_bid,
                '30m': float(res[0][0]) - latest_bid,
                '60m': float(res[0][0]) - latest_bid,
                '120m': float(res[0][0]) - latest_bid,
                '720m': float(res[0][0]) - latest_bid,
                '1440m': float(res[0][0]) - latest_bid,
                '2880m': float(res[0][0]) - latest_bid
            }
            ask_judg = ask_dict['5m'] + ask_dict['10m'] + ask_dict['15m'] + \
                       ask_dict['30m'] + ask_dict['60m'] + ask_dict['120m'] + \
                       ask_dict['720m'] + ask_dict['1440m'] + ask_dict['2880m']
            bid_judg = bid_dict['5m'] + bid_dict['10m'] + bid_dict['15m'] + \
                       bid_dict['30m'] + bid_dict['60m'] + bid_dict['120m'] + \
                       bid_dict['720m'] + bid_dict['1440m'] + bid_dict['2880m']
            logger.info("End  : UP/DOWN judgement.")

            # 余力取得
            logger.info("Start: get available amount.")
            aaJson = GA.availableAmount()
            apl = int(aaJson['data']['actualProfitLoss']) - int(aaJson['data']['availableAmount'])
            logger.info("End  : get available amount.")

            # 建玉がない場合はレバレッジ取引開始
            if apl == 0:
                print("処理開始")

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
    gmoGetLatestRate()