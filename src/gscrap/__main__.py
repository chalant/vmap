import click

from gscrap import gmap

@click.group()
def cli():
    pass

@cli.command()
@click.argument("directory")
def run(directory):
    gmap.launch(directory)

if __name__ == '__main__':
    cli()