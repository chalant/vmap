from tkinter import *

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


import tkinter as tk
from tkinter import ttk



app = tk.Tk()
app.geometry('200x100')
vr = tk.StringVar(app)

# defining the callback function (observer)
def my_callback(var, indx, mode):
    print("Traced variable {}".format(vr.get()))

labelTop = tk.Label(app, text="Choose your favourite month")
labelTop.grid(column=0, row=0)
r = [i for i in range(25)]
comboExample = ttk.Combobox(app, values=r, textvariable=vr)
comboExample.grid(column=0, row=1)
comboExample.current(1)

vr.trace_add("write", my_callback)

app.mainloop()
