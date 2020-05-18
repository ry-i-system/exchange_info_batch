# ビットコイン取引バッチ

### 概要

このプログラムは以下バッチを動作させるものです。

* ビットコインの最新レート取得
* テーブル作成／定義変更
* 自作ライブラリの単体テスト

### 動作環境

|OS|DB|言語|
|:---|:---|:---|
|CentOS 7|MariaDB 5.5|Python 3.8|

### ファイルの配置

```
app_home/
       ├ bin/
       │   ├  migration.py             # テーブル作成／定義変更
       │   └  get_latest_rate.py       # 最新レート取得
       ├ conf/
       │   └  config.py                # DB接続設定情報・RESTAPI接続情報
       ├ lib/
       │   ├  __init__.py              # モジュールをロードするのに必要
       │   ├  db_access.py             # DB接続ライブラリ
       │   └  gmo_api.py               # RESTAPI接続ライブラリ
       ├ log/                          # ログ出力先
       ├ migration/        
       │   └  *.sql                    # テーブル作成／定義変更SQLファイル
       ├ tests/        
       │   └  test_*.py                # 単体テストコード
       └ Pipfile                       # 使うライブラリを列挙
```

### デプロイ手順

1. アプリケーションを格納するディレクトリに移動し、Gitリポジトリをクローン
```
$ cd $app_home
$ git clone https://github.com/ry-i-system/exchange_info_batch.git
```
2. 必要なPythonライブラリをインストール
```
$ pip install pipenv
$ pipenv install
```
3. Python実行環境にスイッチ
```
$ pipenv shell
```

### 設定情報記述

`conf/config.py`の各パラメータに記述
```python
class DatabaseConf(object):
    hostName = "localhost"
    dbName = "db_name"
    userId = "user_id"
    passWord = "pass_word"

class EndpointConf(object):
    pubUrl = "https://xxx.xxx.xxx.com/public"
    priUrl = "https://xxx.xxx.xxx.com/private"
    apiKey = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    secretKey = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

### バッチ実行方法

* `get_latest_rate.py`の場合
```
$ cd $app_home
$ python bin/get_latest_rate.py -f "gmo" -o "BTC_JPY"
```

* `exec_leverage_trade.py`の場合
```
$ cd $app_home
$ python bin/exec_leverage_trade.py -f "gmo" -o "BTC_JPY"
```

* `migration.py`の場合 (引数は migration/ に格納したSQLファイル名　※拡張子.sqlは除く)
```
$ cd $app_home
$ python bin/migration.py -f "sql_file_name"
```

### 単体テスト実行方法

OK が表示されればテスト実行は成功です。

* `test_file_name.py`の場合
```
$ cd $app_home
$ python tests/test_file_name.py
```

* 全単体テストのファイルをまとめて実行する場合
```
$ cd $app_home
$ python -m unittest discover tests "test_*.py"
...
----------------------------------------------------------------------
Ran 3 tests in 0.292s

OK
```