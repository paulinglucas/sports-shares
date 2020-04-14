from django.shortcuts import render
from held_shares.models import InvestedGame, InvestedShare
from odds_update.views import calculateProfit
from exchanges.models import Request

# Create your views here.
def getUserHistory(user):
    context = {}
    context['profit'] = calculateProfit()
    inv_shares = InvestedShare.objects.filter(user=user)
    inv_games = InvestedGame.objects.filter(user=user)
    sell_requests = Request.objects.filter(sender=user.profile)
    buy_requests = Request.objects.filter(receiver=user.profile)
