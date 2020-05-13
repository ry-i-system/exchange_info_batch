import sys,os
import unittest

# ../libをロードパスに入れる
app_home = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)) , ".." ))
sys.path.append(os.path.join(app_home,"lib"))

# ../テスト対象のライブラリのロード
from db_access import DbAccess as DA

class TestDbMigrate(unittest.TestCase):

    def test_dbMigrate(self):
        # SQL取得
        f = open(app_home + "/migration/create_table_eip_unit_test.sql")
        data = f.read()
        sql = data.replace('\n','')
        f.close()
        
        # 想定結果
        res_test = "Success"

        # テスト実行
        self.assertEqual(res_test, DA.dbMigrate(sql))

        # SQL取得
        f = open(app_home + "/migration/drop_table_eip_unit_test.sql")
        data = f.read()
        sql = data.replace('\n','')
        f.close()
        
        # 想定結果
        res_test = "Success"

        # テスト実行
        self.assertEqual(res_test, DA.dbMigrate(sql))

if __name__ == '__main__':
    unittest.main()
