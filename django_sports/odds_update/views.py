from django.shortcuts import render
from held_shares.models import InvestedShare, InvestedGame
from exchanges.models import Request
from decimal import Decimal

# Create your views here.
def calculateProfit(request):
    held_shares = InvestedShare.objects.filter(user=request.user)
    held_games = InvestedGame.objects.filter(user=request.user)
    soldExchanges = Request.objects.filter(sender=request.user.profile).filter(hidden=True).exclude(salePrice=-1.00)

    profit = 0

    for share in held_shares:
        profit -= float(share.boughtAt)*share.numSharesHeld
        if share.share.win:
            profit += float(share.numSharesHeld)*10

    for game in held_games:
        profit -= float(game.amountUsed)
        if game.game.gameOver:
            if game.bet == 1 and game.game.didHomeWin:
                profit += game.amountUsed*game.oddsAtPurchase
            elif game.bet == 2 and game.game.didAwayWin:
                profit += game.amountUsed*game.oddsAtPurchase
            elif game.bet == 3 and game.game.didHomeSpread:
                profit += game.amountUsed*game.oddsAtPurchase
            elif game.bet == 4 and game.game.didAwaySpread:
                profit += game.amountUsed*game.oddsAtPurchase

    for exchange in soldExchanges:
        profit += float(exchange.salePrice)*exchange.numShares
        profit -= float(exchange.inv_share.boughtAt)*exchange.numShares

    profit = round(profit, 2)
    request.user.profile.current_profit = profit
    request.user.profile.save()
