# ################################
# 取引所：GMOコイン
# 処理名：ビットコイン最新レート取得
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
@click.option('--optional_arg','-o',default="None")
def gmoGetLatestRate(must_arg,optional_arg):
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
        logger.info(f"must_arg = {must_arg}")
        logger.info(f"optional_arg = {optional_arg}")

        # 取引所ステータス取得
        status = GA.exStatus()

        # 取引所がOPENの場合
        if status == "OPEN":
            logger.info("The exchange is open.")
            logger.info("Start getting the latest rate.")
            latestRateJson = GA.latestRate("BTC_JPY")

            # 登録データ定義
            ex_cd = f"{must_arg}"
            ask = latestRateJson['data'][0]['ask']
            bid = latestRateJson['data'][0]['bid']
            high = latestRateJson['data'][0]['high']
            last = latestRateJson['data'][0]['last']
            low = latestRateJson['data'][0]['low']
            symbol = latestRateJson['data'][0]['symbol']
            volume = latestRateJson['data'][0]['volume']
            val = [ex_cd, ask, bid, high, last, low, symbol, volume]
            logger.info("Acquisition of the latest rate has been completed.")

            # DB接続
            logger.info("Start DB registration.")
            # SQL
            sql = "INSERT INTO eip_latest_rate (ex_cd, ask, bid, high, last, low, symbol, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

            res = DA.dbAccess(sql, val)
            logger.info("DB registration completed.")
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