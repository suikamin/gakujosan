# セットアップ用の処理を書くファイルです。

import os, sys, json
import consts

# setupをします
def setup():
    # exe化の判定
    isFrozen = getattr(sys, 'frozen', False)
    # 同梱ブラウザのパスをPlaywrightに教える設定（環境変数にplaywrightのパスを設定）
    if isFrozen:
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(sys._MEIPASS, "ms-playwright")

# 設定情報の読み込みと保存
def load_config() :
    """
    起動時にconfig.jsonが存在しているなら、ファイルを開く
    """
    if os.path.exists(consts.CONFIG_PATH):
        with open(consts.CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None