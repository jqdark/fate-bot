# FateBot


## Contents
- [Introduction](#introduction)
- [Setup](#setup)
- [Planned Improvements](#planned-improvements)
- [License](#license)

## Introduction

Discord dice-rolling bot for the Dark Heresy 2 RPG system.

Written in Python using: [discord.py](https://github.com/Rapptz/discord.py), [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy), and [Lark](https://github.com/lark-parser/lark).

Key features:

- Optional "fast mode" allows the `--roll` command prefix to be omitted (set on a per-channel basis).

- Simple command interface for performing DH2 skill/characteristic tests.

![Screenshot of a DH skill test](/examples/basic_tests.png?raw=true)

- Persistent storage of character profiles.

![Screenshot of DH skill tests](/examples/skill_tests.png?raw=true)

- Roll arbitrary combinations of dice.

![Screenshot of generic dice rolls](/examples/generic.png?raw=true)

- Save command macros for later reuse.

![Screenshot of a macro](/examples/macro.png?raw=true)

- Autocorrection of misspelled skill and characteristic names.

![Screenshot of spell correction](/examples/autocorrect.png?raw=true)

## Setup

Make sure you have Python (3.9 or newer) and Pipenv installed.

Create the environment and install dependencies:

    $ pipenv install

Make a `.env` file in the root directory to provide your Discord bot token.

You may also optionally specify an alternate database url (defaults to "sqlite:///fate.db").

    DISCORD_TOKEN=YOUR.DISCORD.BOT.TOKEN
    DB_URL=OPTIONAL.DATABSE.URL

Create your database tables if needed (you only need to do this the first time):

    $ pipenv run python app.py create-tables

Then start the bot:

    $ pipenv run python app.py start

## Planned Improvements

Short term:
- Document dice rolling commands.
- Expand test coverage (and look at using [Hypothesis](https://github.com/HypothesisWorks/hypothesis/tree/master/hypothesis-python) for parser testing).
- Move the case-insensitive wrapping of macro and profile names from `database.py` to `models.py`
- Refactor `rolls.py` and `locations.py`.
- Improve output from `--help`, `--list`, and `--show` commands. 

Long term:
- Make web dashboard GUI for easy character profile and command macro management.
- Expand dice equation parser to handle more general computations.
- Add game rules customisation options (on a per-channel basis).
- Considering adding caching for channel settings (e.g. "is_fast" query). Is it significantly faster than db lookup? Note: this is safe because, even with sharding, each channel can only ever have one worker.
- Migrate to [asyncio SQLAlchemy engine](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html).

## License

Licensed under [MIT](/LICENSE).