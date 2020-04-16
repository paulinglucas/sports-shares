from django.shortcuts import render
from held_shares.models import InvestedShare, InvestedGame
from exchanges.models import Request
from decimal import Decimal

# Create your views here.
def calculateProfit(user):
    held_shares = InvestedShare.objects.filter(user=user)
    held_games = InvestedGame.objects.filter(user=user)
    soldExchanges = Request.objects.filter(sender=user.profile).filter(hidden=True).exclude(salePrice=-1.00)

    profit = 0

    for share in held_shares:
        profit -= float(share.boughtAt)*share.numSharesHeld
        if share.share.win:
            profit += float(share.numSharesHeld)*10

    for game in held_games:
        profit -= float(game.amountUsed)
        if game.game.gameOver:
            if game.bet == 1 and game.game.didHomeWin:
                profit += float(game.amountUsed)*game.oddsAtPurchase
            elif game.bet == 2 and game.game.didAwayWin:
                profit += float(game.amountUsed)*game.oddsAtPurchase
            elif game.bet == 3 and game.game.didHomeSpread:
                profit += float(game.amountUsed)*game.oddsAtPurchase
            elif game.bet == 4 and game.game.didAwaySpread:
                profit += float(game.amountUsed)*game.oddsAtPurchase

    for exchange in soldExchanges:
        profit += float(exchange.salePrice)*exchange.numShares
        profit -= float(exchange.inv_share.boughtAt)*exchange.numShares

    profit = round(profit, 2)
    user.profile.current_profit = profit
    user.profile.save()
    return profit

def calculateTotalShareProfit():
    profit = 0
    for share in InvestedShare.objects.all():
        profit += share.numSharesHeld*float(share.boughtAt)
    return profit
