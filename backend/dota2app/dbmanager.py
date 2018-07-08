"""Logic related to data
"""
import re
from datetime import timedelta

from django.conf import settings


from .remote_apis import OpenDotaAPI


def _find_account_id(api, player):
    """Find account_id for player
    """
    if not player:
        raise ValueError('Not a valid player')
    match = re.match(r'^\d+$', player)
    if match:
        account_id = player
    else:
        account_id = None
    return api.get_account_id(account_id=account_id, username=player)


def get_players_rank(players, date_range):
    """Rank players based on win/lose rate
    """
    def sortkey(el):
        s = el['rank']['win'] + el['rank']['lose']
        if s == 0:
            return 0
        return -el['rank']['win'] / s

    if not players:
        raise ValueError('Players cannot be empty')
    players = list(set(players))
    if len(players) < 2:
        raise ValueError('There should be at least 2 players')
    api = OpenDotaAPI(apikey=getattr(settings, 'OPENDOTA_APIKEY'))
    player_accs = [
        (player, _find_account_id(api, player)) for player in players
    ]
    mapping = {
        '1w': 7,
        '1m': 30,
        '1y': 365,
    }
    if date_range in mapping:
        date_range = timedelta(days=mapping[date_range])
    else:
        date_range = None
    ret = []
    for player, account_id in player_accs:
        ret.append({
            'input': player,
            'account_id': account_id,
            'rank': api.get_player_wl(account_id, date_range)
        })
    return sorted(ret, key=sortkey)


def compare_players(players):
    """Compare 2 players
    """
    if not players:
        raise ValueError('Players cannot be empty')
    players = list(set(players))
    if len(players) != 2:
        raise ValueError('Only 2 players can be compared at one time')
    api = OpenDotaAPI(apikey=getattr(settings, 'OPENDOTA_APIKEY'))
    player_accs = [
        (player, _find_account_id(api, player)) for player in players
    ]
    ret = []
    for player, account_id in player_accs:
        ret.append({
            'input': player,
            'account_id': account_id,
            'rank': api.get_player_wl(account_id)
        })
    return ret


def recommend_hero(player):
    """Recommend a hero for player
    """
    def sortkey(el):
        if el['games'] == 0:
            return 0
        return -el['win'] / el['games']

    if not player:
        raise ValueError('Player must be supplied')
    api = OpenDotaAPI(apikey=getattr(settings, 'OPENDOTA_APIKEY'))
    player_acc = _find_account_id(api, player)
    heroes = api.get_player_heroes(player_acc)
    if not heroes:
        hero = {}
    else:
        hero = sorted(heroes, key=sortkey)[0]
    return {
        'input': player,
        'account_id': player_acc,
        'recommended_hero': hero
    }
