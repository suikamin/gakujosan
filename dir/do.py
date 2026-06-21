import tkinter as tk
from tkinter import messagebox
from plyer import notification
from playwright.sync_api import sync_playwright
from . import consts, otpgen



# --- 3. 自動ログイン ---
def auto_login(config):

    # ==== Chromiumの実行 ====
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless = False,
            args=["--start-maximized"]
            )
        context = browser.new_context(
            no_viewport=True,
            accept_downloads=True
            )

        page = context.new_page()

        # ===== ログインのtry =====
        try:
            # ログインページへ
            page.goto(consts.URI)
            print("debug: 学情まで行きました")

            # 自動入力
            page.fill('input[name="userName"]', config["username"]["rawData"])
            page.fill('input[name="password"]', config["password"]["rawData"])
            page.click('button[type="submit"]')
            print("debug: クリックまでしました")

            # =======================================================
            #  どちらの画面が先に来るかを判定するIF文
            # =======================================================
            # 1. 2段階認証の入力欄を指すセレクター
            otp_selector = 'input[name="ninshoCode"]'

            # 5秒間、どちらかの要素が画面に現れるのをループで監視する
            is_otp_page = False
            
            for _ in range(50):  # 0.1秒 × 50回 ＝ 最大5秒待つ
                # パターンA：もし認証コード入力欄が見つかったら
                if page.locator(otp_selector).is_visible():
                    is_otp_page = True
                    break
                    
                page.wait_for_timeout(100) # 0.1秒待つ

            print("debug: 二段階認証の前まで来ました")

            otp_code = otpgen.gen_otp(secret_key=config["secret_key"]["rawData"].strip().upper())
            # --- 判定後の条件分岐（IF） ---
            if is_otp_page:

                print("debug: 2段階認証画面が表示されました。コードを入力します。")
                page.fill('input[name="ninshoCode"]', value=otp_code)
                page.click('button[class="sw10 sh2"]')

            else:
                print("debug: 2段階認証はスキップされました。")
        
            print("info: ログインに成功しました．")            

            while True:
                if page.is_closed():
                    break
                page.wait_for_timeout(1000)

        except Exception as e:
            print(f"ブラウザが終了しました．: {e}")
        finally:
            browser.close()
            print("info: アプリを終了します．")