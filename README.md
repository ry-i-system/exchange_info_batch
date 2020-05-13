# ビットコイン取引バッチ

### 概要

このプログラムは以下バッチを動作させるものです。

* ビットコインの最新レート取得
* テーブル作成／定義変更
* 自作ライブラリの単体テスト

### 推奨動作環境

|OS|DB|言語|
|:---|:---|:---|
|CentOS 7|MariaDB 5.5|Python 3.8|

### ファイルの配置

```
app_home/
       ├ bin/
       │   ├  migration.py             # テーブル作成／定義変更
       │   └  gmo_get_latest_rate.py   # 最新レート取得
       ├ conf/
       │   └  config.py                # DB接続設定情報・RESTAPI接続情報
       ├ lib/
       │   ├  __init__.py              # モジュールをロードするのに必要
       │   ├  db_access.py             # DB接続ライブラリ
       │   └  gmo_api.py               # RESTAPI接続ライブラリ
       ├ tests/        
       │   └  test_*.py                # 単体テストコード
       ├ migration/        
       │   └  *.sql                    # テーブル作成／定義変更SQLファイル
       ├ log/                          # ログ出力先
       └ Pipfile                       # 使うライブラリを列挙
```

### バッチ実行方法

* `gmo_get_latest_rate.py`の場合
```
$ cd $app_home
$ python3 bin/gmo_get_latest_rate.py -f gmo
```

* `migration.py`の場合 (引数は migration/ に格納したSQLファイル名　※拡張子.sqlは除く)
```
$ cd $app_home
$ python3 bin/migration.py -f "sql_file_name"
```
