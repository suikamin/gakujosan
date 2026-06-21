from dir.setup import load_config
import sys, os, subprocess

from dir.do import auto_login
from dir.gui import InputWindow
from dir.setup import save_json


config = {
    "username" : {"displayName": "学情ID", "rawData": ""},
    "password" : {"displayName": "パスワード", "rawData": ""},
    "secret_key" : {"displayName": "秘密鍵", "rawData": ""}
}

config = load_config()

window = InputWindow(inputDict=config)
window.show()
print("debug:", window.inputDict)

confing = window.inputDict;
save_json(config)
auto_login(config)