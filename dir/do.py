import pyotp ,os, subprocess, json, sys, platform
import tkinter as tk
from tkinter import messagebox
from plyer import notification
from playwright.sync_api import sync_playwright

# === 同梱ブラウザのパスをPlaywrightに教える設定 ===
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS 
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
        "secret" : (secret.replace(" ", "")).strip()
    }

    notification.notify(
        title="設定保存中...",
        message="この操作には数秒かかることがあります...",
        app_name="gakujosan"
        )
    
    # すでにファイルが存在する場合、上書きできるように一旦属性を解除する
    if os.path.exists(CONFIG_FILE):
        try:
            subprocess.run(["attrib", "-h", "-r", CONFIG_FILE])
        except Exception as e:
            print(e)

    # JSONの書き込み
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    print("config.jsonの編集が完了しました．")

    # 再び隠しファイル＆読み取り専用に設定
    try:
        subprocess.run(["attrib", "+h", "+r", CONFIG_FILE])
    except Exception as e:
        print(e)

def get_windows_download_dir():
    """Windowsの標準『ダウンロード』フォルダのパスを安全に取得する関数"""
    return os.path.join(os.environ["USERPROFILE"], "Downloads")

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

    tk.Button(root, text="設定を保存してログインを開始", command=on_submit, bg="#4CAF50", fg="white").pack(pady=20)
    root.mainloop()

# --- 3. 自動ログイン ---
def auto_login():
    config = load_config()
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
        show_setup_gui(existing_config=load_config())
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