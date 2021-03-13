from tkinter import *

root = Tk()

my_var = StringVar(root, "N/A")
options = OptionMenu(root, my_var)
canvas = Canvas(root, width=80, height=80, bg="white")


# defining the callback function (observer)
def my_callback(var, indx, mode):
    print("Traced variable {}".format(my_var.get()))

# registering the observer
my_var.trace_add('write', my_callback)

Label(root, textvariable=my_var).pack(padx=5, pady=5)

options.pack(padx=5, pady=5)
# canvas["height"] = 4
# canvas["width"] = 6
canvas.pack(padx=2, pady=2)

root.mainloop()