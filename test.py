import tkinter as tk

root = tk.Tk()

menuBar = tk.Menu(root)
menu1 = tk.Menu(root)
submenu = tk.Menu(root)

var1 = tk.StringVar()
var2 = tk.StringVar()

submenu.add_radiobutton(label="Option 1", variable=var1)
submenu.add_radiobutton(label="Option 2", variable=var2)

menuBar.add_cascade(label="Menu 1", menu=menu1)
menu1.add_cascade(label="Submenu with radio buttons", menu=submenu)

root.config(menu=menuBar)
root.mainloop()