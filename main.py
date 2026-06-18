from dir import show_setup_gui, load_config, auto_login
from plyer import notification
import sys, os, keyboard, subprocess

if __name__ == "__main__" :
    is_reset_mode = ("-r" in sys.argv or "--reset" in sys.argv) or keyboard.is_pressed("ctrl")
    is_clear_mode = "-c" in sys.argv or "--clear" in sys.argv

    if is_reset_mode:
        show_setup_gui(existing_config=load_config())
   
    elif is_clear_mode:   
        CONFIG_FILE = "config.json"
        if os.path.exists(CONFIG_FILE):
            try:
                subprocess.run(["attrib", "-h", "-r", CONFIG_FILE])
                os.remove(CONFIG_FILE)
            except Exception as e:
                print(e)
        else:
            print(f"{CONFIG_FILE}が見つかりませんでした")
            sys.exit()

    elif load_config() is None:
        show_setup_gui(existing_config=None)

    else:
        auto_login()