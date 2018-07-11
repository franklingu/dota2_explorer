"""Request information for opendota
"""
import time
import random

import requests


class OpenDotaAPI(object):
    """Request data from OpenDota"""
    def __init__(self, apikey):
        # Seems valid apikey is not required to get responses
        if not apikey:
            # raise ValueError('apikey cannot be empty')
            pass
        self.apikey = apikey

    def get_pro_players(self):
        """Get a list of pro players
        """
        return self.get('proPlayers')

    def get_player(self, account_id):
        """Get player account info
        """
        return self.get('players/{}'.format(account_id))

    def get_player_matches(self, account_id, date_range=None):
        """Get player matches
        """
        if date_range is None:
            params = {}
        else:
            params = {'date': date_range.days}
        return self.get('players/{}/matches'.format(account_id), params=params)

    def get_player_wl(self, account_id, date_range=None):
        """Get player win/lose
        """
        if date_range is None:
            params = {}
        else:
            params = {'date': date_range.days}
        return self.get('players/{}/wl'.format(account_id), params=params)

    def get_player_heroes(self, account_id):
        """Get player heros
        """
        return self.get('players/{}/heroes'.format(account_id))

    def get_account(self, account_id=None, username=None, strict=False):
        """Get player account_id
        """
        if username is None and account_id is None:
            raise ValueError('Cannot search for such player')
        try:
            return self.get_player(account_id)
        except ValueError:
            pass
        matches = self.get('searchES', params={'q': username})
        if not matches:
            raise ValueError('Cannot search for such player')
        if not strict:
            return matches[0]
        for match in matches:
            if match['personaname'] == username:
                return match
        raise ValueError('Cannot search for such player')

    def get(self, url, params=None, retry=3, sleep=30):
        """Making get request to OpenDota
        """
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
