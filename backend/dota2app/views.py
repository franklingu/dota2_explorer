"""Views for dota2app
"""
import csv

from rest_framework.views import APIView
from rest_framework.response import Response as APIResponse
from rest_framework import status as HTTPStatus


from . import dbmanager

class GetPlayersView(APIView):
    """Get list of players based on name or account_id
    """
    def get(self, request):
        message, status, data = 'ok', 200, {}
        try:
            players = request.query_params.get('players')
            if not players:
                raise ValueError('Players param is required')
            players = list(csv.reader([players]))[0]
            drange = request.data.get('range')
            data = dbmanager.get_players_rank(players, drange)
        except ValueError as err:
            message = str(err)
            status = HTTPStatus.HTTP_400_BAD_REQUEST
        return APIResponse({'message': message, 'data': data}, status=status)


class ComparePlayersView(APIView):
    """Compare players' skills
    """
    def get(self, request):
        message, status, data = 'ok', 200, {}
        try:
            players = request.query_params.get('players')
            if not players:
                raise ValueError('Players param is required')
            players = list(csv.reader([players]))[0]
            data = dbmanager.compare_players(players)
        except ValueError as err:
            message = str(err)
            status = HTTPStatus.HTTP_400_BAD_REQUEST
        return APIResponse({'message': message, 'data': data}, status=status)


class RecommendHeroView(APIView):
    """Recommend hero for player
    """
    def get(self, request):
        message, status, data = 'ok', 200, {}
        try:
            player = request.query_params.get('player')
            if not player:
                raise ValueError('Player param is required')
            data = dbmanager.recommend_hero(player)
        except ValueError as err:
            message = str(err)
            status = HTTPStatus.HTTP_400_BAD_REQUEST
        return APIResponse({'message': message, 'data': data}, status=status)
