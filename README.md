# Cro Bot

A discord bot used for my personal usage. Currently a work in progress.
Avatar for this project is Cro from [ChronoClock](https://www.youtube.com/watch?v=oWz-ROOOSUE)

## Features

The current main feature includes a search for sdvx.in. More will be added as time goes along.

### Prerequisites

There are quite a few requirements for this bot:
* Python 3.5+ ; Lowest version tested: 3.6
* [discord.py](https://github.com/Rapptz/discord.py)
* [sqlalchemy](https://www.sqlalchemy.org/)
* [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy)
* [Unidecode](https://pypi.org/project/Unidecode/)
* [aiohttp](https://aiohttp.readthedocs.io/en/stable/)
* [kytea (python)](https://github.com/chezou/Mykytea-python)
* [romkan](https://pypi.org/project/romkan/)


To properly use kytea, a model file is required. You can obtain one from the [kytea
source](http://www.phontron.com/kytea/#download).


### Set up

#### General setup

1. Add a discord bot token to the config file, ``settings.ini``

#### Features
sdvxin:

1. Run ``recreate_db()`` from ``CroBot/features/sdvxin/database`` to create an sqlite3 database
2. Run ``update()`` from ``CroBot/features/sdvxin/sdvx`` to fetch songs for the database
3. Edit the configuration file for an api key for azure's cognitive translation features
4. Obtain a kytea model, name it ``model.bin``, and place it in the same directory as ``run.py``

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [sym3tri for their Japanese regex](https://gist.github.com/sym3tri/980083)
* KSM Discord
