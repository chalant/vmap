from tkinter import *
from tkinter.ttk import *


class GFG:
    def __init__(self, master=None):
        self.master = master

        # to take care movement in x direction
        self.x = 1
        # to take care movement in y direction
        self.y = 0

        # canvas object to create shape
        self.canvas = Canvas(master)
        # creating cz
        self.rectangle = self.canvas.create_rectangle(
            5, 5, 25, 25, fill="black")
        self.canvas.pack()

        # calling class's movement method to
        # move the cz
        self.movement()

    def movement(self):
        # This is where the move() method is called
        # This moves the cz to x, y coordinates
        self.canvas.move(self.rectangle, self.x, self.y)

        self.canvas.after(100, self.movement)

        # for motion in negative x direction

    def left(self, event):
        print(event.keysym)
        self.x = -5
        self.y = 0

    # for motion in positive x direction
    def right(self, event):
        print(event.keysym)
        self.x = 5
        self.y = 0

    # for motion in positive y direction
    def up(self, event):
        print(event.keysym)
        self.x = 0
        self.y = -5

    # for motion in negative y direction
    def down(self, event):
        print(event.keysym)
        self.x = 0
        self.y = 5


if __name__ == "__main__":
    # # object of class Tk, resposible for creating
    # # a tkinter toplevel window
    # master = Tk()
    # gfg = GFG(master)
    #
    # # This will bind arrow keys to the tkinter
    # # toplevel which will navigate the image or drawing
    # master.bind("<KeyPress-Left>", lambda e: gfg.left(e))
    # master.bind("<KeyPress-Right>", lambda e: gfg.right(e))
    # master.bind("<KeyPress-Up>", lambda e: gfg.up(e))
    # master.bind("<KeyPress-Down>", lambda e: gfg.down(e))
    #
    # # Infnite loop breaks only by interrupt
    # mainloop()
    from tkinter import *

    import tkinter as tk

    root = tk.Tk()
    canvas = tk.Canvas(root, width=300, height=300, scrollregion=(0, 0, 5000, 1000))
    canvas.pack(fill="both", expand=True)

    canvas.create_rectangle(600, 700, 650, 750, fill="red")
    canvas.yview_moveto(700 / 1000)
    canvas.xview_moveto(600 / 5000)

    root.mainloop()