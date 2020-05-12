# ################################
# 処理名：DB接続
# 作成日：2020/04/30
# ################################

import sys
import os
import json
import MySQLdb

# 親ディレクトリをアプリケーションのホーム(${app_home})に設定
app_home = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)) , ".." ))
# ${app_home}をライブラリロードパスに追加
sys.path.append(os.path.join(app_home))

# 設定クラスのロード
from conf.config import DatabaseConf as DC

class DbAccess(object):
    # DB接続（参照系）
    def dbSelect(sql):
        try:
            # DB接続
            connection = MySQLdb.connect(
                user=DC.userId,
                passwd=DC.passWord,
                host=DC.hostName,
                db=DC.dbName,
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor)
            cursor = connection.cursor()

            # SQL実行
            cursor.execute(sql)

            # 結果を取り出す
            data = cursor.fetchall()

            # DB切断
            cursor.close()
            connection.close()
            return data

        except ZeroDivisionError as e:
            # DB切断
            cursor.close()
            connection.close()
            print('catch ZeroDivisionError:', e)
            return False

    # DB接続（更新系）
    def dbAccess(sql, val):
        try:
            # DB接続
            connection = MySQLdb.connect(
                user=DC.userId,
                passwd=DC.passWord,
                host=DC.hostName,
                db=DC.dbName)
            cursor = connection.cursor()

            # SQL
            cursor.execute(sql,val)

            # DB切断
            connection.commit()
            cursor.close()
            connection.close()
            return True

        except ZeroDivisionError as e:
            # DB切断
            connection.rollback()
            cursor.close()
            connection.close()
            print('catch ZeroDivisionError:', e)
            return False

    # DBテーブル作成／定義変更
    def dbMigrate(sql):
        try:
            # DB接続
            connection = MySQLdb.connect(
                user=DC.userId,
                passwd=DC.passWord,
                host=DC.hostName,
                db=DC.dbName)
            cursor = connection.cursor()

            # SQL
            cursor.execute(sql)

            # DB切断
            connection.commit()
            cursor.close()
            connection.close()
            return "Success"

        except ZeroDivisionError as e:
            # DB切断
            connection.rollback()
            cursor.close()
            connection.close()
            print('catch ZeroDivisionError:', e)
            return "Failure"