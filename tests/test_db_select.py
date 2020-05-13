import sys,os
import unittest

# ../libをロードパスに入れる
app_home = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)) , ".." ))
sys.path.append(os.path.join(app_home,"lib"))

# ../テスト対象のライブラリのロード
from db_access import DbAccess as DA

class TestDbSelect(unittest.TestCase):

    def test_dbSelect(self):
        # SQL文
        sql = "SELECT * FROM eip_latest_rate"
        
        # 想定結果
        res_test = ()

        # テスト実行
        self.assertEqual(res_test, DA.dbSelect(sql))

if __name__ == '__main__':
    unittest.main()
