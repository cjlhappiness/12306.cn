# coding=utf-8


"""
    12306GUI
"""


import tkinter
from datetime import date
import query12306


train_content_l_list = []
gtop = tkinter.Tk()  # 根窗口
gtop.title("12306 QUERY")
gtop.geometry('1100x400+100+100')


def start():
    glist.delete(1, tkinter.END)
    trafficInformations = query12306.assemble_query_result(gtkf.get(), gtkt.get(), gtkd.get(), seatFilter=range(13))
    for x in range(len(trafficInformations)):
        trafficInformation = trafficInformations[x]
        glist.insert(x + 1, trafficInformation)


gtkf = tkinter.Entry(gtop)
gtkf.insert(0, "杭州")
gtkf.pack()
gtkt = tkinter.Entry(gtop)
gtkt.insert(0, "杭州")
gtkt.pack()
gtkd = tkinter.Entry(gtop)
gtkd.insert(0, date.today())
gtkd.pack()
gbtn = tkinter.Button(gtop, text="开始", command=start)
gbtn.pack()
glist = tkinter.Listbox(gtop, width=150, height=150)
glist.pack()
glist.insert(0, query12306.echo_query_title())

gtop.mainloop()
