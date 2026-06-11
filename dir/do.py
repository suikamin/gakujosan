import pyotp
import os
import json
import subprocess
import sys
import tkinter as tk
import platform
from tkinter import messagebox
from playwright.sync_api import sync_playwright

# === 同梱ブラウザのパスをPlaywrightに教える設定 ===
if getattr(sys, 'frozen', False):
    # exe化されて実行されている場合
    bundle_dir = sys._MEIPASS #_MEIPASS: exeによって実行されているときだけ作成される特別な変数
    # Playwrightがブラウザを探すフォルダを、exe内部の一時展開先に固定する
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(bundle_dir, "ms-playwright")

CONFIG_FILE = "config.json"

# --- 1. 設定情報の読み込みと保存 ---
def load_config() :
    """
    起動時にconfig.jsonが存在しているなら、ファイルを開く
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_config(url, username, password, secret) :
    config = {
        "url" : url,
        "username" : username,
        "password" : password,
        "secret" : secret.replace(" ", "")
    }
    
    # すでにファイルが存在する場合、上書きできるように一旦属性を解除する
    if os.path.exists(CONFIG_FILE):
        try:
            if platform.system() == "Windows":
                # Windows用の処理
                subprocess.run(["attrib", "-h", "-r", CONFIG_FILE])
            else:
                # Mac / Linux用の処理
                # 1. 先頭にドットをつけてリネーム
                os.rename(CONFIG_FILE, f".{CONFIG_FILE}")
                # 2. 権限変更
                os.chmod(f".{CONFIG_FILE}", 0o400)
        except Exception as e:
            print(e)

    # JSONの書き込み
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    print("config.jsonの編集が完了しました．")

    # 再び隠しファイル＆読み取り専用に設定
    try:
        if platform.system() == "Windows":
            # Windows用の処理
            subprocess.run(["attrib", "+h", "+r", CONFIG_FILE])
        else:
            # Mac / Linux用の処理
            # 1. 先頭のドットを消す
            os.rename(CONFIG_FILE, f"{CONFIG_FILE}")
            # 2. 権限変更
            os.chmod(f".{CONFIG_FILE}", 0o644)
    except Exception as e:
        print(e)

# --- 2. 初回起動 ---
def show_setup_gui(existing_config=None):
    def on_submit():
        url = entry_url.get()
        user = entry_user.get()
        pw = entry_pw.get()
        sec = entry_sec.get()

        if not (url and user and pw and sec):
            messagebox.showwarning("入力エラー", "すべての項目を入力してください。")
            return
        
        save_config(url, user, pw, sec)
        messagebox.showinfo("成功", "設定を保存しました。自動ログインを開始します。")
        root.destroy()
        auto_login()

    root = tk.Tk()
    root.title("Campussquare 自動ログイン設定")
    root.geometry("450x320")

    # 既存の設定がある場合はそれを初期値にし、なければ空文字にする
    init_url = "https://gakujo.iess.niigata-u.ac.jp/campusweb/campusportal.do"
    init_user = existing_config.get("username", "") if existing_config else ""
    init_pw = existing_config.get("password", "") if existing_config else ""
    init_sec = existing_config.get("secret", "") if existing_config else ""

    tk.Label(root, text="Campussquare ログインURL:").pack(pady=5)
    entry_url = tk.Entry(root, width=50)
    entry_url.insert(0, init_url)
    entry_url.pack()

    tk.Label(root, text="学籍番号:").pack(pady=5)
    entry_user = tk.Entry(root, width=50)
    entry_user.insert(0, init_user)
    entry_user.pack()

    tk.Label(root, text="パスワード:").pack(pady=5)
    entry_pw = tk.Entry(root, width=50, show="*")
    entry_pw.insert(0, init_pw)
    entry_pw.pack()

    tk.Label(root, text="Google Authenticator 秘密鍵:").pack(pady=5)
    entry_sec = tk.Entry(root, width=50)
    entry_sec.insert(0, init_sec)
    entry_sec.pack()

    tk.Button(root, text="設定を保存してログイン", command=on_submit, bg="#4CAF50", fg="white").pack(pady=20)
    root.mainloop()

# --- 3. 自動ログイン ---
def auto_login():
    config = load_config()
    if not config: 
        return
    
    try:
        totp = pyotp.TOTP(config["secret"])
        otp_code = totp.now()
    except Exception as e:
        print(f"秘密鍵エラー: {e}")
        return
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        try:
            # ログインページへ
            page.goto(config["url"])

            # 自動入力
            page.fill('input[name="userName"]', config["username"])
            page.fill('input[name="password"]', config["password"])
            page.click('button[type="submit"]')

            try:
                page.wait_for_selector('input[name="ninshoCode"]')
                page.fill('input[name="ninshoCode"]', otp_code)
                page.click('button[class="sw10 sh2"]')
            except:
                print("二段階認証は不要でした．")

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