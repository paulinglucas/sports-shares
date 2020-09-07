from django.shortcuts import render
from held_shares.models import InvestedShare, InvestedGame
from exchanges.models import Request
from decimal import Decimal
from history.models import Payment

# Create your views here.
def calculateProfit(user):
    held_shares = InvestedShare.objects.filter(user=user)
    soldExchanges = Request.objects.filter(sender=user).exclude(salePrice=-1.00)
    boughtExchanges = Request.objects.filter(receiver=user).exclude(salePrice=-1.00)
    held_games = InvestedGame.objects.filter(user=user.user)
    payments = Payment.objects.filter(payer=user)

    profit = 0

    for share in held_shares:
        if share.share.win:
            profit += float(share.numSharesHeld)*10

    for exchange in soldExchanges:
        profit += float(exchange.salePrice)*exchange.numShares
    for exchange in boughtExchanges:
        profit -= float(exchange.salePrice)*exchange.numShares

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

    for payment in payments:
        profit += float(payment.amount_paid)

    profit = round(profit, 2)
    user.current_profit = profit
    user.save()
    return profit

def calculateTotalShareProfit():
    profit = 0
    for share in Request.objects.filter(sender__username="BallStreet"):
        profit += share.numShares*float(share.salePrice)
    return profit
