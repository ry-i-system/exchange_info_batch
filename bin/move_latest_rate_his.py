# ################################
# 処理名：過去データを履歴テーブルに移動
# 作成日：2020/11/01
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

# コマンドライン実行・引数なし
@click.command()
def moveLatestRateHis():
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

        # 処理開始
        logger.info("Start move the latest rate for history table.")

        # DB接続
        logger.info("Start DB registration.")
        
        # 履歴テーブルにデータコピーSQL
        sql = "INSERT INTO eip_latest_rate_his SELECT * FROM eip_latest_rate WHERE datetime < CURRENT_TIMESTAMP + INTERVAL - 3 DAY"
        res = DA.dbAccess(sql, val)

        # コピーしたデータ削除SQL
        sql = "DELETE FROM eip_latest_rate WHERE datetime < CURRENT_TIMESTAMP + INTERVAL - 3 DAY"
        res = DA.dbAccess(sql, val)
        logger.info("DB registration completed.")

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
    moveLatestRateHis()