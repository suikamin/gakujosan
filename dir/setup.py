# セットアップ用の処理を書くファイルです。

import os, sys, json
from . import consts, gui
from plyer import notification

# setupをします
def setup():
    # exe化の判定
    isFrozen = getattr(sys, 'frozen', False)
    # 同梱ブラウザのパスをPlaywrightに教える設定（環境変数にplaywrightのパスを設定）
    if isFrozen or isFrozen == False: # テスト用に偽でもif分が実行されるようにしました。
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(sys._MEIPASS, "ms-playwright")

# 設定情報の読み込みと保存
def load_config():
    # config.jsonの存在確認及びロード
    if os.path.exists(consts.CONFIG_PATH) == False:
        # json作成のfuncに移動
        return None
    
    with open(consts.CONFIG_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("json形式が不正です。当該jsonを削除し、アプリケーションを再起動してください。")
            return None

def save_json(config):
    try:
        with open(consts.CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        print("info: 保存に成功しました")
    
    except TypeError as e:
        print(f"fatal: jsonに変換できない型が含まれています: {e}")
    except Exception as e:
        print(f"fatal: 予期しないエラーが発生しました: {e}")