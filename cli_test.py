import click

@click.group()
def cli():
    pass

@cli.command()
@click.argument("name")
def initdb(name):
    click.echo('Initialized the database')
    click.echo(name)

@cli.command()
def dropdb():
    click.echo('Dropped the database')

if __name__ == '__main__':
    cli()