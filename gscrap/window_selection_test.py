import tkinter as tk

from tools import window_selection as ws

window = tk.Tk()

window.title("Welcome to LikeGeeks app")

# Set geometry
window.geometry("200x200")

selector = ws.WindowSelector(window)

def select_window():
    selector.start_selection(on_selected, on_abort, on_error)

def on_selected(event):
    win_id = event.window_id
    selector.resize_window(win_id, 400, 400)

def on_abort():
    print("Aborted!!!")

def on_error():
    print("Error!!")

tk.Button(window, text="Select Window", font=("Helvetica 15 bold"), command=select_window).pack()

if __name__ == '__main__':
    window.mainloop()



