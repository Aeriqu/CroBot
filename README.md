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


## Set up

### Docker setup

1. Install [Docker](https://docs.docker.com/get-docker/)
2. Set up a settings.ini file using [the one in the repo](https://github.com/Aeriqu/CroBot/blob/master/settings.ini) as a template.
3. Run ``docker run -d -v crobot_db:/app/sdvxCharts.db -v /path/to/your/settings.ini:/app/settings.ini aeriqu/crobot``

### Traditional setup

#### General setup

1. Add a discord bot token to the config file, ``settings.ini``

#### Features
sdvxin:

1. Obtain a kytea model, name it ``model.bin``, and place it in the same directory as ``run.py``
2. Run ``db_init.py`` to initialize the database
3. Execute ``!sdvxin update`` in a channel with the bot to download the metadata from sdvx.in (this will take a while)
4. Edit the configuration file for an api key for azure's cognitive translation features


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [sym3tri for their Japanese regex](https://gist.github.com/sym3tri/980083)
* KSM Discord
