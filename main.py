from dir import show_setup_gui, load_config, auto_login
import sys

if __name__ == "__main__" :
    is_reset_mode = "-r" in sys.argv or "--reset" in sys.argv

    if is_reset_mode:
        show_setup_gui(existing_config=load_config())
    
    elif load_config() is None:
        show_setup_gui(existing_config=None)

    else:
        auto_login()