from django.urls import path

from . import views

urlpatterns = [
    path(
        'get_players/',
        views.GetPlayersView.as_view(),
        name='get_players'
    ),
    path(
        'compare_players/',
        views.ComparePlayersView.as_view(),
        name='compare_players'
    ),
    path(
        'recommend_hero/',
        views.RecommendHeroView.as_view(),
        name='recommend_hero'
    ),
]
