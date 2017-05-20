# -*- coding: utf-8 -*-

"""
    This module implements the GUI of FtpSiteSearchEngine.

    :author: Sam Yang (samyangcoder@gmail.com)
    :license: MIT
"""

from tkinter import *
import search
import logging
logging.basicConfig(level=logging.INFO)


# Application 是组件容器，继承自 Frame
class Application(Frame):
    # master 是父组件(widget)，可选，传递给 Application 的实例
    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.promptText = Label(text='please input ip range you want to search below', font='"Comic Sans MS" 24')
        self.promptText.place(x=138, y=100)
        logging.info('[gui module]promptText width is %s' % self.promptText.winfo_reqwidth())

        self.ipFrom = Entry(width=30, justify=CENTER)
        self.ipFrom.place(x=99, y=200)
        logging.info('[gui module]ipFrom/ipTo width is %s' % self.ipFrom.winfo_reqwidth())

        self.divider = Label(text='—')
        self.divider.place(x=390, y=202)

        self.ipTo = Entry(width=30, justify=CENTER)
        self.ipTo.place(x=417, y=200)

        self.searchButton = Button(width=20, text='Search', command=self.send_input)
        self.searchButton.place(x=296, y=300)
        logging.info('[gui module]searchButton width is %s' % self.searchButton.winfo_reqwidth())

        self.loading = Label(text='searching...', font='"Comic Sans MS" 24')

    def send_input(self):
        ip_from = self.ipFrom.get()
        ip_to = self.ipTo.get()

        # 清除界面
        for widget in self.master.place_slaves():
            widget.place_forget()
        logging.info('[gui module]loading width is %s' % self.loading.winfo_reqwidth())
        self.loading.place(x=334, y=280)

        self.loading.after(5, search.search, self, ip_from, ip_to)  # 在指定毫秒数后执行回调，以使执行回调前先渲染loading

app = Application()
app.master.title('FTP Site Search Engine')
app.master.geometry('800x600+200+100')  # `800x600`是窗口大小，`+200+100`为窗口位置
app.mainloop()
