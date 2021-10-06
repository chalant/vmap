import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo

# def selected(var, idx, mode):
#     print(var, idx, mode)
#
# # create the root window
# root = tk.Tk()
# root.geometry('200x100')
# root.resizable(False, False)
# root.title('Listbox')
#
# root.columnconfigure(0, weight=1)
# root.rowconfigure(0, weight=1)
#
# # create a list box
# langs = ['Java', 'C#', 'C', 'C++', 'Python',
#         'Go', 'JavaScript', 'PHP', 'Swift']
#
# langs_var = tk.StringVar(value=langs)
#
# listbox = tk.Listbox(
#     root,
#     height=6,
#     selectmode='browse')
#
#
# listbox.insert(0, "Nachos")
# listbox.insert(2, "Sandwich")
# listbox.insert(3, "Burger")
# listbox.insert(4, "Pizza")
# listbox.insert(5, "Burrito")
#
# listbox.grid(
#     column=0,
#     row=0,
#     sticky='nwes'
# )
#
# # link a scrollbar to a list
# scrollbar = ttk.Scrollbar(
#     root,
#     orient='vertical',
#     command=listbox.yview
# )
#
# listbox['yscrollcommand'] = scrollbar.set
#
# scrollbar.grid(
#     column=1,
#     row=0,
#     sticky='ns')
#
# # handle event
#
#
#
# def items_selected(event):
#     """ handle item selected event
#     """
#     # get selected indices
#     selected_indices = listbox.curselection()
#     print(selected_indices)
#     # get selected items
#     selected_langs = ",".join([listbox.get(i) for i in selected_indices])
#     msg = f'You selected: {selected_langs}'
#
#     showinfo(
#         title='Information',
#         message=msg)
#
#
# listbox.bind('<<ListboxSelect>>', items_selected)
#
# root.mainloop()

# import tkinter as tk
# from tkinter import ttk
# from tkinter.messagebox import showinfo

root = tk.Tk()
root.geometry('300x200')
root.resizable(False, False)
root.title('Combobox Widget')


def month_changed(event):
    msg = f'You selected {month_cb.get()}!'
    showinfo(title='Result', message=msg)


# month of year
months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

label = ttk.Label(text="Please select a month:")
label.pack(fill='x', padx=5, pady=5)

# create a combobox
selected_month = tk.StringVar()

month_cb = ttk.Combobox(root, textvariable=selected_month)
month_cb['values'] = months
month_cb['state'] = 'readonly'  # normal
month_cb.pack(fill='x', padx=5, pady=5)

month_cb.bind('<<ComboboxSelected>>', month_changed)

root.mainloop()