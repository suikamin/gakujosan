from dir.setup import load_config
import sys, os, subprocess

from dir.do import config
from dir.gui import InputWindow
from dir.setup import save_json

window = InputWindow(inputDict=config)
window.show();
print("debug:", window.inputDict)

confing = window.inputDict;
save_json(config)
