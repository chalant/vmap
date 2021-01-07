import tkinter as tk

class Editing(object):
    # when a rectangle is selected, we can modify its dimensions, or drag it
    # when changing its dimensions, the all instances of the base triangle are
    # updated and redrawn. Also, all instances of the base are highlighted as-well.

    # if we click outside a rectangle, we move back to drawing state

    # todo: need an editor (draw squares at each corner of the rectangle and the center)
    #  the center is for dragging an the corners are for resizing
    def __init__(self, manager, collision):
        """

        Parameters
        ----------
        manager: controllers.tools.mapping.MappingTool
        """
        self._manager = manager

        self._root = None

        self._options = m = tk.Menu(self._manager.canvas, tearoff=False)

        m.add_command(label="Reset", command=self._on_reset)
        m.add_separator()
        m.add_command(label="Cancel", command=self._on_cancel)
        m.add_command(label="Done", command=self._on_done)

        m.entryconfig("Reset", state="disabled")

    def on_right_click(self, event):
        res = self._manager.select_rectangle(event.x, event.y)

        options = self._options

        options.tk_popup(event.x_root, event.y_root)

        if res:
            options.entryconfig("Reset", state="normal")
        else:
            options.entryconfig("Reset", state="disabled")

    def _on_close(self):
        self._root.destroy()

    def _selected_label(self, label_id):
        # set label id
        self._manager.rectangle.label_id = label_id

    def _on_cancel(self):
        # todo: clear everything
        if self._manager.previous_state:
            # go back to previous state if any
            self._manager.state = self._manager.previous_state
        else:
            self._manager.state = self._manager.initial

    def _on_done(self):
        # todo update the selected rectangle coordinates
        self._on_cancel()

    def _on_reset(self):
        # todo: move back to initial rectangle dimensions and location
        #  and stay in edit state
        pass

    def update(self):
        self._options.entryconfig("Reset", state="disabled")