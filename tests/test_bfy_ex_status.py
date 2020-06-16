import sys,os
import unittest

# ../libをロードパスに入れる
app_home = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)) , ".." ))
sys.path.append(os.path.join(app_home,"lib"))

# ../テスト対象のライブラリのロード
from bfy_api import BfyApi as BA

class TestBfyExStatus(unittest.TestCase):

    def test_exStatus(self):
        # 想定結果
        res_test = "NORMAL"

        # テスト実行
        self.assertEqual(res_test, BA.exStatus())

if __name__ == '__main__':
    unittest.main()
