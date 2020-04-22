#
# translate.py
# Wraps Microsoft API for translation
# Uses kytea for transliteration
#


from CroBot.features.sdvxin import regex

import configparser
import aiohttp
import json
import re

import Mykytea
import romkan

# Configuration parser object
config = configparser.ConfigParser()
config.read('settings.ini')
key = config['microsoft']['key']

api_endpoint = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from=ja&to=en'


####################
#    TRANSLATE     #
####################


async def fetch_post(link, headers, body):
    """
    fetch_get: The helper function for AIOHTTP which creates a session and then posts information from the link
    :param link: The link to fetch from
    :return: the text from the request
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(link, headers=headers, json=body) as response:
            return await response.text()


async def translate(text):
    """
    translate: Retrieves the Japanese -> English translation from the Microsoft API.
    :param text: The text to be translated
    :return: The translated string
             The error on error request
    """
    # Create a request, send it, and get a response
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Content-type': 'application/json',
    }
    body = [{
        'text': text
    }]
    request = await fetch_post(api_endpoint, headers=headers, body=body)
    response = json.loads(request)

    # Error checking
    if 'error' in response:
        return 'Error ' + str(response['error']['code']) + ': ' + response['error']['message']

    return response[0]['translations'][0]['text']


####################
#  TRANSLITERATE   #
####################


def transliterate_pick_best(characters):
    """
    transliterate_pick_best: Picks the best choice for transliteration from tags created from kytea
                                - Returns the original if it isn't in kanji to begin with, because the hiragana
                                - If kanji, return the tag that is hiragana
    :param characters: Characters split
    :return: The best picked character
    """
    # Fetch the original phrase
    original = characters[0]

    # Check to see if there is kanji in the phrase, if so, return the hiragana that matches up
    if re.search(regex.kanji, original):
        for character in characters:
            if re.search(regex.kanji, character) is None:
                return character

    # If the phrase is already hiragana, then return hiragana
    return original


async def transliterate(text):
    """
    transliterate: Retrieves the Japanese transliteration via kytea
    :param text: The text to be transliterated
    :return: The transliterated string
    """
    # Create a kytea object that loads in model
    mk = Mykytea.Mykytea('-model model.bin')

    # split up the text
    split = mk.getTagsToString(text).split(' ')

    transliterated = ''

    # Loop through the split up parts, find equivalent hiragana, and add it to the transliterated string
    for word in split:
        if len(word) > 0:
            characters = word.split('/')
            transliterated += transliterate_pick_best(characters)

    # Convert the hiragana string into a romaji string then return it
    return romkan.to_roma(transliterated)
