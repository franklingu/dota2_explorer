"""Logic related to data
"""
import re
from datetime import datetime, timedelta

import pandas as pd
from sklearn import linear_model
from django.conf import settings

from .remote_apis import OpenDotaAPI
from .models import (Player, PlayerMatch, PlayerHero)


g_api = OpenDotaAPI(apikey=getattr(settings, 'OPENDOTA_APIKEY'))


def _find_account_id(player):
    """Find account_id for player
    """
    if not player:
        raise ValueError('Not a valid player')
    match = re.match(r'^\d+$', player)
    if match:
        account_id = player
    else:
        account_id = None
    return Player.objects.get_account_id(
        g_api, account_id=account_id, username=player
    )


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
    player_accs = [
        (player, _find_account_id(player)) for player in players
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
            'rank': PlayerMatch.objects.get_player_wl(
                g_api, account_id, date_range
            ),
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
    player_accs = [
        (player, _find_account_id(player)) for player in players
    ]
    ret = []
    for player, account_id in player_accs:
        ret.append({
            'input': player,
            'account_id': account_id,
            'rank': PlayerMatch.objects.get_player_wl(g_api, account_id)
        })
    return ret


class RecommendHeroBaseModel(object):
    def recommend(self, player_acc):
        raise NotImplementedError('To be implemented')


class RecommendHeroSimpleModel(RecommendHeroBaseModel):
    def recommend(self, player_acc):
        def sortkey(el):
            if el['games'] == 0:
                return 0
            return -el['win'] / el['games']

        heroes = PlayerHero.objects.get_player_heroes(g_api, player_acc)
        if not heroes:
            hero = {}
        else:
            hero = {
                'hero_id': sorted(heroes, key=sortkey)[0]['hero_id']
            }
        return hero


class RecommendHeroLogisticModel(RecommendHeroBaseModel):
    def recommend(self, player_acc):
        def extract_win(row):
            if ((row.player_slot < 128 and row.radiant_win) or
                    (row.player_slot >= 128 and not row.radiant_win)):
                return 1
            return 0

        def extract_weight(row):
            return 1 - 0.01 * (
                datetime.now() - datetime.fromtimestamp(row.start_time)
            ).days / 30

        matches = PlayerMatch.objects.get_player_matches(g_api, player_acc)
        df = pd.DataFrame(matches)
        # determine player win: if slot < 128, then player is radiant
        df['win'] = df.apply(extract_win, axis=1)
        # assign weight based on timestamp, the older the game, the less important
        df['weight'] = df.apply(extract_weight, axis=1)
        # filter out leavers and heros with low appearance
        df2 = df[df.leaver_status < 1]
        filtered_heroes = set(
            df2[['hero_id', 'win']].groupby('hero_id').filter(
                lambda x: len(x) > 2
            ).hero_id
        )
        df3 = df2[df2.hero_id.isin(filtered_heroes)]
        # build input data frame
        df4 = pd.get_dummies(df3.hero_id.astype('category'))
        df5 = df3[['kills', 'deaths', 'assists', 'hero_id', 'win', 'weight']]
        df6 = pd.concat([df5, df4], axis=1)
        logreg = linear_model.LogisticRegression(C=1e5)
        X = df6[['kills', 'deaths', 'assists'] + list(df4.columns)]
        Y = df6[['win']]
        logreg.fit(X, Y)
        pred = logreg.predict(X)
        # taking win rate here as the single factor. However, frequent hero
        # should be considered as well
        final_result = pd.concat(
            [df6.hero_id, pd.Series(pred, index=df6.index, name='pred_win')],
            axis=1
        ).groupby('hero_id').mean()
        recommends = list(final_result[
            final_result.pred_win == final_result.pred_win.max()
        ].index)
        if not recommends:
            return {'hero_id': None}
        return {'hero_id': recommends[0]}


def recommend_hero(player):
    """Recommend a hero for player
    """
    if not player:
        raise ValueError('Player must be supplied')
    player_acc = _find_account_id(player)
    hero = RecommendHeroLogisticModel().recommend(player_acc)
    return {
        'input': player,
        'account_id': player_acc,
        'recommended_hero': hero
    }
