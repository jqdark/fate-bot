from os import getenv
import click

from fate import FastBot, FateCog, Database
from fate.database.legacy import YAMLDatabase


DISCORD_TOKEN = getenv("DISCORD_TOKEN")
DB_URL = getenv("DB_URL", "sqlite:///fate.db")

database = Database(DB_URL)

cog = FateCog(database)

bot = FastBot(
    database,
    command_prefix="--",
    fast_command=cog.roll
)

bot.add_cog(cog)


@click.group()
def cli():
    pass


@cli.command()
def start():
    """Run the bot."""

    bot.run(DISCORD_TOKEN)


@cli.command()
def create_tables():
    """Create database tables."""

    database.create_tables()


@cli.command()
@click.argument("filename")
def load_legacy(filename):
    """Import data from legacy YAML file."""

    legacy = YAMLDatabase(filename)
    legacy.save_all(database)


if __name__ == "__main__":
    cli()