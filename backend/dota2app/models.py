from datetime import datetime, timedelta
try:
    import simplejson as json
except ImportError:
    import json

from pytz import timezone
from django.db import models
from django.conf import settings


g_refresh_delta = timedelta(
    seconds=getattr(settings, 'API_REFRESH_PERIOD', 3600 * 24)
)
g_timezone = timezone(
    getattr(settings, 'TIME_ZONE', 'Asia/Singapore')
)


class PlayerManager(models.Manager):
    def from_response(self, res):
        account_id = res.get('profile', {}).get('account_id')
        personname = res.get('profile', {}).get('personaname')
        if not account_id or not personname:
            raise ValueError('Not a valid account')
        player, created = self.get_or_create(account_id=account_id)
        player.account_id = account_id
        player.personname = personname
        player.response = json.dumps(res)
        player.save()
        return player

    def get_account_id(self, api, account_id, username):
        # account id is primary_key, if match found then account_id found
        if account_id is not None:
            result = self.filter(account_id=account_id)
            if result:
                return account_id
        result = self.filter(personname=username)
        if result and not result[0].should_refresh():
            return result[0].account_id
        res = api.get_account(account_id, username)
        return self.from_response(res).account_id


class Player(models.Model):
    account_id = models.IntegerField(primary_key=True)
    personname = models.CharField(max_length=256, db_index=True)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PlayerManager()

    def should_refresh(self):
        return self.updated_at - g_timezone.localize(
            datetime.now()
        ) > g_refresh_delta


class PlayerMatchManager(models.Manager):
    def from_response(self, res, account_id):
        ret = []
        for match_detail in res:
            match_id = match_detail['match_id']
            match, created = self.get_or_create(
                account_id=account_id, match_id=match_id
            )
            match.account_id = account_id
            match.match_id = match_id
            match.response = json.dumps(match_detail)
            match.save()
            ret.append(match)
        return ret

    def get_player_wl(self, api, account_id, date_range=None):
        def get_wl(matches, date_range):
            win, lose = 0, 0
            for match in matches:
                match_detail = json.loads(match.response)
                start = datetime.fromtimestamp(match_detail['start_time'])
                if start + date_range < datetime.now():
                    continue
                player_slot = match_detail['player_slot']
                radiant_win = match_detail['radiant_win']
                if ((player_slot < 128 and radiant_win) or
                        (player_slot >= 128 and not radiant_win)):
                    win += 1
                else:
                    lose += 1
            return {'win': win, 'lose': lose}

        matches = self.filter(account_id=account_id)
        if matches and not matches[0].should_refresh():
            return get_wl(matches, date_range)
        res = api.get_player_matches(account_id)
        matches = self.from_response(res, account_id)
        return get_wl(matches, date_range)

    def get_player_matches(self, api, account_id, date_range=None):
        def get_matches(matches, date_range):
            ret = []
            for match in matches:
                match_detail = json.loads(match.response)
                start = datetime.fromtimestamp(match_detail['start_time'])
                if date_range and start + date_range < datetime.now():
                    continue
                ret.append(match_detail)
            return ret

        matches = self.filter(account_id=account_id)
        if matches and not matches[0].should_refresh():
            return get_matches(matches, date_range)
        res = api.get_player_matches(account_id)
        matches = self.from_response(res, account_id)
        return get_matches(matches, date_range)


class PlayerMatch(models.Model):
    match_id = models.IntegerField()
    account = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='matches'
    )
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PlayerMatchManager()

    class Meta:
        index_together = (('account', 'match_id'))
        unique_together = (('account', 'match_id'))

    def should_refresh(self):
        return self.updated_at - g_timezone.localize(
            datetime.now()
        ) > g_refresh_delta


class PlayerHeroManager(models.Manager):
    def from_response(self, res, account_id):
        ret = []
        for hero_detail in res:
            hero_id = hero_detail['hero_id']
            match, created = self.get_or_create(
                account_id=account_id, hero_id=hero_id
            )
            match.account_id = account_id
            match.hero_id = hero_id
            match.response = json.dumps(hero_detail)
            match.save()
            ret.append(match)
        return ret

    def get_player_heroes(self, api, account_id):
        def get_heroes(heroes):
            ret = []
            for hero in heroes:
                ret.append(json.loads(hero.response))
            return ret

        heroes = self.filter(account_id=account_id)
        if heroes and not heroes[0].should_refresh():
            return get_heroes(heroes)
        res = api.get_player_heroes(account_id)
        heroes = self.from_response(res, account_id)
        return get_heroes(heroes)



class PlayerHero(models.Model):
    hero_id = models.IntegerField()
    account = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name='heroes'
    )
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PlayerHeroManager()

    class Meta:
        index_together = (('account', 'hero_id'))
        unique_together = (('account', 'hero_id'))

    def should_refresh(self):
        return self.updated_at - g_timezone.localize(
            datetime.now()
        ) > g_refresh_delta
