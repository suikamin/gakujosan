# セットアップ用の処理を書くファイルです。

# exe化の判定
isFrozen = getattr(sys, 'frozen', False)
# 同梱ブラウザのパスをPlaywrightに教える設定（環境変数にplaywrightのパスを設定）
if isFrozen:
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(sys._MEIPASS, "ms-playwright")