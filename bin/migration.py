# ################################
# 処理名：DBテーブル作成／定義変更
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

# コマンドライン引数のハンドリング. must_argは必須オプション、optional_argは任意オプション
@click.command()
@click.option('--migration_file', '-m', required=True)
def migration(migration_file):
    # 自身の名前から拡張子を除いてプログラム名(${prog_name})にする
    prog_name = os.path.splitext(os.path.basename(__file__))[0]

    # ロガーの設定

    # フォーマット
    log_format = logging.Formatter("%(asctime)s [%(levelname)8s] %(message)s")
    # レベル
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
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
        logger.info(f"migration_file = {migration_file}")

        # SQL取得
        f = open(app_home + f"/migration/{migration_file}.sql")
        data = f.read()
        sql = data.replace('\n','')
        f.close()

        logger.info(DA.dbMigrate(sql))

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
    migration()
