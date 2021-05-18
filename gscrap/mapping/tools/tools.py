from abc import abstractmethod, ABC

from tkinter import ttk
import tkinter as tk

class Tool(ABC):
    @abstractmethod
    def get_view(sel, container):
        raise NotImplementedError

    @abstractmethod
    def start_tool(self, project):
        raise NotImplementedError

    @abstractmethod
    def clear_tool(self):
        raise NotImplementedError


class ToolsView(object):
    def __init__(self, container, controller):
        self.frame = frame = tk.Frame(container)
        self.tabs = tabs = ttk.Notebook(frame)

        tabs.bind("<<NotebookTabChanged>>", controller.on_tab_selected)
        tabs.pack(expand=1, fill=tk.BOTH)

        frame.pack(expand=1, fill=tk.BOTH)

class ToolsController(object):
    def __init__(self, container):
        self._tools = {}

        self._view = ToolsView(container, self)

        self._current_tool = None

        self._project = None

    def add_tool(self, tool, name):
        view = self._view
        frame = tool.get_view(view.tabs)

        view.tabs.add(frame, text=name)

        self._tools[name] = tool

        root = view.tabs.winfo_toplevel()
        root.wm_minsize(800, frame.winfo_height())

    def set_project(self, project):
        self._project = project

        ct = self._current_tool

        #clear and load data for the tool
        if ct:
            tool = self._tools[ct]
            tool.clear_tool()
            tool.start_tool(project)

    def on_tab_selected(self, event):
        selected = event.widget.select()
        name = event.widget.tab(selected, "text")

        ct = self._current_tool
        tools = self._tools

        #clear any loaded data (samples etc.) and mouse bindings etc.
        if ct != None:
            tools[ct].clear_tool()

        self._current_tool = name

        project = self._project

        #start tool if a project has been set.
        if project:
            #load data etc.
            tools[name].start_tool(project)