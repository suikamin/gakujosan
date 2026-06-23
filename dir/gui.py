# config設定用のguiを表示するスクリプトです

import tkinter as tk

class InputWindow:

    def __init__(self, inputDict: dict[str, dict[str, str]]):
        self.inputDict = inputDict
        self.root = tk.Tk()

        self.ui_wigets: dict[str, tk.Entry] = {}
    
    def whenSubmitted(self) :
        for key, value in self.inputDict.items():
            self.inputDict[key]["rawData"] = self.ui_wigets[key].get()
        self.destroy()
        print(self.inputDict[key]["rawData"])
        return self.inputDict
    
    def show(self):
        for key, value in self.inputDict.items():
            tk.Label(self.root, text=value["displayName"]).pack()
            print(value["displayName"])
            self.ui_wigets[key] = tk.Entry(self.root)
            self.ui_wigets[key].insert(0, self.inputDict[key]["rawData"])
            self.ui_wigets[key].pack()

        button = tk.Button(self.root, text="ログイン", command=self.whenSubmitted)
        button.pack()
        self.root.mainloop();

    def destroy(self):
        self.root.destroy()