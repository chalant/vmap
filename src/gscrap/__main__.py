import click

from gscrap import gmap

@click.group()
def cli():
    pass

@cli.command()
@click.argument("project_name")
@click.argument("directory")
def run(project_name, directory):
    gmap.launch(project_name, directory)

if __name__ == '__main__':
    cli()