# from tkinter import *

# root = Tk()
#
# my_var = StringVar(root, "N/A")
# options = OptionMenu(root, my_var)
# canvas = Canvas(root, width=80, height=80, bg="white")
#
#
# # defining the callback function (observer)
# def my_callback(var, indx, mode):
#     print("Traced variable {}".format(my_var.get()))
#
# # registering the observer
# my_var.trace_add('write', my_callback)
#
# Label(root, textvariable=my_var).pack(padx=5, pady=5)
#
# options.pack(padx=5, pady=5)
# # canvas["height"] = 4
# # canvas["width"] = 6
# canvas.pack(padx=2, pady=2)
#
# root.mainloop()


import  tkinter as tk

from tkinter import *
from tkinter import ttk

# Creating the root window


# import tkinter as tk
# from tkinter import ttk
#
#
#
# app = tk.Tk()
# app.geometry('200x100')
# vr = tk.StringVar(app)
#
# # defining the callback function (observer)
# def my_callback(var, indx, mode):
#     print("Traced variable {}".format(vr.get()))
#
# labelTop = tk.Label(app, text="Choose your favourite month")
# labelTop.grid(column=0, row=0)
# r = [i for i in range(25)]
# comboExample = ttk.Combobox(app, values=r, textvariable=vr)
# comboExample.grid(column=0, row=1)
# comboExample.current(1)
# comboExample["state"] = tk.DISABLED
#
# vr.trace_add("write", my_callback)
#
# app.mainloop()

# try:
#     # Python2
#     import Tkinter as tk
# except ImportError:
#     # Python3
#     import tkinter as tk
#
# def toggle():
#     '''
#     use
#     t_btn.config('text')[-1]
#     to get the present state of the toggle button
#     '''
#     if t_btn.config('relief')[-1] == 'sunken':
#         t_btn.config(relief='raised')
#     else:
#         t_btn.config(relief='sunken')
#
# root = tk.Tk()
#
# t_btn = tk.Button(text="True", width=12, command=toggle)
# t_btn.pack(pady=5)
#
# root.mainloop()

# from tkinter import *
#
# def sel():
#    selection = "You selected the option " + str(var.get())
#    label.config(text = selection)
#
# root = Tk()
# var = IntVar()
# R1 = Radiobutton(root, text="Option 1", variable=var, value=1,
#                   command=sel)
# R1.pack( anchor = W )
#
# R2 = Radiobutton(root, text="Option 2", variable=var, value=2,
#                   command=sel)
# R2.pack( anchor = W )
#
# R3 = Radiobutton(root, text="Option 3", variable=var, value=3,
#                   command=sel)
# R3.pack( anchor = W)
#
# label = Label(root)
# label.pack()
# root.mainloop()

# import pytesseract
# from PIL import Image
# import cv2
# import numpy as np
#
# path = "/home/yves/.gmap/images/a6ec059c607740798dc3a30d3ea2a528"
# im = Image.open(path)
#
# kernel = np.ones((3,3),np.uint8)
#
# a, b = cv2.threshold(cv2.cvtColor(np.asarray(im), cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY_INV)
# b = cv2.erode(b, kernel)
# im = Image.fromarray(b)
#
# im.show()
#
# res = pytesseract.image_to_string(im)
# print(res)

# from tkinter import *
#
# master = Tk()
#
# var = tk.IntVar(master, value=100)
#
# i = 1
#
# def max_val():
#     global i
#     w.config(to=i)
#     i += 1
#
# w = Spinbox(master, from_=0, command=max_val)
# w.pack()
#
# mainloop()

# import tkinter as tk
#
# def callback(selection):
#     print(selection)
#     options.set(selection)
#
# root = tk.Tk()
# options = tk.StringVar()
# menu = tk.Menubutton(root, options, 'a', 'b', 'c', command = callback)
# menu.pack()
# menu['menu'].add_command(label = 'New Item', command = lambda: callback('New Item'))
# options.set('a')
# root.mainloop()

from tkinter import *

def callback():
    print("Hello!")

top = Tk()

mb = Menubutton(top, text="condiments", relief=FLAT)
mb.grid()
mb.menu =  menu = Menu(mb, tearoff = 0)
mb["menu"] = mb.menu

menu.add_command(label="Test", command=callback)

# mayoVar = IntVar()
# ketchVar = IntVar()
#
# mb.menu.add_checkbutton ( label="mayo",
#                           variable=mayoVar )
# mb.menu.add_checkbutton ( label="ketchup",
#                           variable=ketchVar )

mb.pack()
top.mainloop()


