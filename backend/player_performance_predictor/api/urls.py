from django.urls import path
from .views import PlayerPredictionView, home

urlpatterns = [
    path('predictions/<int:req_season>/', PlayerPredictionView.as_view(), name='player-predictions'),
    path('', home, name='home'),
]