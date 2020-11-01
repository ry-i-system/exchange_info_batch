import sys,os
import unittest

# ../libをロードパスに入れる
app_home = os.path.abspath(os.path.join( os.path.dirname(os.path.abspath(__file__)) , ".." ))
sys.path.append(os.path.join(app_home,"lib"))

# ../テスト対象のライブラリのロード
from gmo_api import GmoApi as GA

class TestPositionSummary(unittest.TestCase):

    def test_positionSummary(self):
        # 想定結果
        res_test = {}
        # 実際の結果
        res = GA.positionSummary("BTC_JPY")

        # テスト実行
        self.assertEqual(res_test, res)

if __name__ == '__main__':
    unittest.main()
