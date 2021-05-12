from abc import abstractmethod, ABC

from tkinter import ttk

class Tool(ABC):
    @abstractmethod
    def get_view(self):
        raise NotImplementedError

    @abstractmethod
    def start_tool(self, project):
        raise NotImplementedError

    @abstractmethod
    def clear_tool(self):
        raise NotImplementedError


class ToolsView(object):
    def __init__(self, container, controller):
        self.tabs = tabs = ttk.Notebook(container)

        tabs.bind("<<NotebookTabChanged>>", controller.on_tab_selected)

        tabs.pack(expand=1, fill="both")

class ToolsController(object):
    def __init__(self, container):
        self._tools = {}

        self._view = ToolsView(container, self)

        self._current_tool = None

        self._project = None

    def add_tool(self, tool, name):
        self._view.tabs.add(tool.get_view(), text=name)
        self._tools[name] = tool

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
        if ct:
            tools[ct].clear()

        self._current_tool = name

        project = self._project

        #start tool if a project has been set.
        if project:
            #load data etc.
            tools[name].start_tool(project)