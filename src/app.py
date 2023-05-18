# -*- coding: utf-8 -*-

import tkinter.messagebox
from datetime import datetime
from tkinter import *

import search

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.ipListLabel = Label(text='Enter IP list (one IP per line):', font='"Comic Sans MS" 14')
        self.ipListLabel.place(x=20, y=20)

        self.ipList = Text(width=30, height=5)
        self.ipList.place(x=20, y=50)

        self.fileTypeLabel = Label(text='Filter by file type (e.g., .txt):', font='"Comic Sans MS" 14')
        self.fileTypeLabel.place(x=20, y=150)

        self.fileType = Entry(width=30)
        self.fileType.place(x=20, y=180)

        self.nameContainsLabel = Label(text='Filter by name contains (e.g., report):', font='"Comic Sans MS" 14')
        self.nameContainsLabel.place(x=20, y=210)

        self.nameContains = Entry(width=30)
        self.nameContains.place(x=20, y=240)

        self.dateRangeLabel = Label(text='Filter by date range (YYYY-MM-DD - YYYY-MM-DD):', font='"Comic Sans MS" 14')
        self.dateRangeLabel.place(x=20, y=270)

        self.dateRange = Entry(width=30)
        self.dateRange.place(x=20, y=300)

        self.sizeRangeLabel = Label(text='Filter by size range (Min - Max in bytes):', font='"Comic Sans MS" 14')
        self.sizeRangeLabel.place(x=20, y=330)

        self.minSize = Entry(width=12)
        self.minSize.place(x=20, y=360)

        self.maxSize = Entry(width=12)
        self.maxSize.place(x=150, y=360)

        self.searchButton = Button(width=10, text='Search', command=self.send_input)
        self.searchButton.place(x=20, y=400)

        self.resultLabel = Label(text='Search Results:', font='"Comic Sans MS" 14')
        self.resultLabel.place(x=300, y=20)

        self.result = Listbox(width=60, height=20)
        self.result.place(x=300, y=50)

        self.loading = Label(text='Searching...', font='"Comic Sans MS" 14', fg='red')
        self.loading.place(x=300, y=400)
        self.loading.grid_remove()

    def send_input(self):
        ip_text = self.ipList.get("1.0", END)
        ip_list = [ip.strip() for ip in ip_text.split('\n') if ip.strip()]
        file_type = self.fileType.get().strip()

        name_contains = self.nameContains.get().strip()
        date_range_str = self.dateRange.get().strip()
        min_size_str = self.minSize.get().strip()
        max_size_str = self.maxSize.get().strip()

        date_range = None
        min_size = None
        max_size = None

        if date_range_str:
            try:
                start_date_str, end_date_str = date_range_str.split('-')
                start_date = datetime.strptime(start_date_str.strip(), '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str.strip(), '%Y-%m-%d')
                date_range = (start_date, end_date)
            except ValueError:
                tkinter.messagebox.showerror("Invalid Date Range", "Please enter a valid date range in the format YYYY-MM-DD - YYYY-MM-DD.")
                return

        if min_size_str:
            try:
                min_size = int(min_size_str)
            except ValueError:
                tkinter.messagebox.showerror("Invalid Minimum Size", "Please enter a valid minimum size in bytes.")
                return

        if max_size_str:
            try:
                max_size = int(max_size_str)
            except ValueError:
                tkinter.messagebox.showerror("Invalid Maximum Size", "Please enter a valid maximum size in bytes.")
                return

        self.loading.grid()
        q = search.Queue()
        self.loading.after(5, search.search, q, ip_list, file_type, name_contains, date_range, min_size, max_size)
        self.loading.after(5, self.show_results, q)

    def show_results(self, q):
        self.loading.grid_remove()
        self.result.delete(0, END)

        ftp_data = q.get()

        if not ftp_data:
            self.result.insert(END, "No results found.")

        for ftp in ftp_data:
            for f in ftp:
                self.result.insert(END, f"{f[0]}: {f[1]}")

app = Application()
app.master.title("FTP Search")
app.master.geometry("800x500")
app.mainloop()
