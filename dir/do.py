import os, subprocess, pyotp
import tkinter as tk
from tkinter import messagebox
from plyer import notification
# from playwright.sync_api import sync_playwright

from . import consts, setup

config = {
    "username" : {"displayName": "学情ID", "rawData": ""},
    "password" : {"displayName": "パスワード", "rawData": ""},
    "secret_key" : {"displayName": "秘密鍵", "rawData": ""}
}

# --- 3. 自動ログイン ---
def auto_login():
    config = setup.load_config()
    if not config: 
        return
    
    # ==== ワンタイムパスワードの生成 ====
    try:
        if (len(config["secret"]) == 32):
            totp = pyotp.TOTP(config["secret"])
            otp_code = totp.now()
        else:
            raise Exception
    except Exception as e:
        print(f"秘密鍵エラー: {e}")
        messagebox.showerror("秘密鍵エラー", f"秘密鍵を再入力してください．または、以下のサイトを参考にOTPを再設定してください．\nhttps://www.iess.niigata-u.ac.jp/acpb/upload/20231016105024000213600.pdf\n{e}")
        # show_setup_gui(existing_config=setup.load_config())
        return
    
    download_dir = get_windows_download_dir()

    notification.notify(
        title = "ブラウザを起動中...",
        message = "起動には数秒かかることがあります...",
        app_name = "gakujosan"
    )

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

        # --- EventListener用の関数 ---
        def handle_download(download):
            "ダウンロードを検知して、正常に保存する"
            try:
                filename = download.suggested_filename
                save_path = os.path.join(download_dir, filename)
                download.save_as(save_path)
                print(f"ダウンロードが完了しました．{filename}")
            
            except Exception as e:
                print(f"ダウンロードエラー: {e}")

        # ==== ダウンロードのEventListender ====
        context.on("download", handle_download)

        # ===== ログインのtry =====
        try:
            # ログインページへ
            page.goto(config["url"])

            # 自動入力
            page.fill('input[name="userName"]', config["username"])
            page.fill('input[name="password"]', config["password"])
            page.click('button[type="submit"]')

            # =======================================================
            #  どちらの画面が先に来るかを判定するIF文
            # =======================================================
            # 1. 2段階認証の入力欄を指すセレクター
            otp_selector = 'input[name="ninshoCode"]'

            # 5秒間、どちらかの要素が画面に現れるのをループで監視する
            is_otp_page = False
            is_skipped = False
            
            for _ in range(50):  # 0.1秒 × 50回 ＝ 最大5秒待つ
                # パターンA：もし認証コード入力欄が見つかったら
                if page.locator(otp_selector).is_visible():
                    is_otp_page = True
                    break
                    
                # パターンB：もし認証コード欄が出ずに、URLが変わったら
                if r"page=main" in page.url:
                    is_skipped = True
                    break
                    
                page.wait_for_timeout(100) # 0.1秒待つ

            # --- 判定後の条件分岐（IF） ---
            if is_otp_page:
                print("2段階認証画面が表示されました。コードを入力します。")
                page.fill('input[name="ninshoCode"]', otp_code)
                page.click('button[class="sw10 sh2"]')

            elif is_skipped:
                print("2段階認証はスキップされました。")

            else:
                print("エラー：5秒経っても認証画面もメニュー画面も確認できませんでした。")
        
            print("ログインが成功しました．")            

            while True:
                if page.is_closed():
                    break
                page.wait_for_timeout(1000)

        except Exception as e:
            print(f"ブラウザが終了しました．: {e}")
        finally:
            browser.close()
            print("アプリを終了します．")