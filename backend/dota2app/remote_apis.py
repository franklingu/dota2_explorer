"""Request information for opendota
"""
import time
import random

import requests


class OpenDota(object):
    def __init__(self, apikey):
        self.apikey = apikey

    def get_pro_players(self):
        return self.get('proPlayers')

    def get_player(self, account_id=None, username=None):
        account_id = self.get_account_id(account_id, username)
        return self.get('players/{}'.format(account_id))

    def get_player_wl(self, account_id=None, username=None, date_range=None):
        if date_range is None:
            params = {}
        else:
            params = {'date': date_range.days()}
        account_id = self.get_account_id(account_id, username)
        return self.get('players/{}/wl'.format(account_id), params=params)

    def get_player_heroes(self, account_id=None, username=None):
        account_id = self.get_account_id(account_id, username)
        return self.get('players/{}/heroes'.format(account_id))

    def get_account_id(self, account_id=None, username=None, strict=False):
        if account_id is not None:
            return account_id
        if username is None:
            raise ValueError('Cannot search for such player')
        matches = self.get('searchES', params={'q': username})
        if not matches:
            raise ValueError('Cannot search for such player')
        if not strict:
            return matches[0]['account_id']
        for match in matches:
            if match['personaname'] == username:
                return match['account_id']
        raise ValueError('Cannot search for such player')

    def get(self, url, params=None, retry=3, sleep=30):
        url = 'https://api.opendota.com/api/' + url
        if params is None:
            params = {}
        params.update({'api_key': self.apikey})
        for retry_i in range(retry):
            try:
                res = requests.get(url, params=params)
                if res.status_code == 200:
                    return res.json()
            except Exception:  #pylint: disable=broad-except
                time.sleep(sleep + retry_i * sleep * random.random())
        raise ValueError('Could not make such request to: {}'.format(url))
