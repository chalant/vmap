import os

import click

from gscrap.data import paths

from gscrap.projects import projects
from gscrap.projects import workspace

@click.group()
def cli():
    pass

@cli.command()
@click.argument("project_name")
@click.argument("directory")
def run(project_name, directory):
    launch(project_name, directory)

def launch(project_name, directory=None):
    if directory == None:
        path = os.getcwd()
    else:
        if '~' in directory:
            path = os.path.expanduser(directory)
        else:
            path = os.path.join(os.getcwd(), directory)

    project = projects.set_project(workspace.WorkSpace(path, project_name))

    paths.set_project(project)

    #temporary fix: we import gmap after setting everything
    from gscrap import gmap

    gmap.MANAGER.start(project)

if __name__ == '__main__':
    cli()