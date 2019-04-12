#
# translate.py
# A simple wrapper for Microsoft's translate API
# Specifically, we are going to use the Japanese -> English translation and romaji transliteration features
# These two features are in the free set, so we'll be using that.
# More information here: https://azure.microsoft.com/en-us/services/cognitive-services/translator-text-api/
#


import configparser
import requests

# Configuration parser object
config = configparser.ConfigParser()
config.read('settings.ini')
key = config['microsoft']['key']

base_endpoint = 'https://api.cognitive.microsofttranslator.com/'
translation_path = 'translate?api-version=3.0&from=ja&to=en'
transliterate_path ='transliterate?api-version=3.0&language=ja&fromScript=Jpan&toScript=Latn'


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
    request = requests.post(base_endpoint + translation_path, headers=headers, json=body)
    response = request.json()

    # Error checking
    if 'error' in response:
        return 'Error ' + response['error']['code'] + ': ' + response['error']['message']

    return response[0]['translations'][0]['text']


async def transliterate(text):
    """
    transliterate: Retrieves the Japanese transliteration from the MicrosoftAPI
    :param text: The text to be transliterated
    :return: The transliterated string
             None on failure
    """
    # Create a request, send it, and get a response
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Content-type': 'application/json',
    }
    body = [{
        'text': text
    }]
    request = requests.post(base_endpoint + transliterate_path, headers=headers, json=body)
    response = request.json()

    # Error checking
    if 'error' in response:
        return 'Error ' + response['error']['code'] + ': ' + response['error']['message']

    return response[0]['text']
