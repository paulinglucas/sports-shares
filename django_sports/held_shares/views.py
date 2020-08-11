from django.shortcuts import render, redirect
from shares.models import Share, Game
from held_shares.models import InvestedShare, InvestedShareManager, InvestedGame
from exchanges.models import PendingSale, Request
from decimal import Decimal
from django.db.models import Sum, Min
from django.http import HttpResponseRedirect

# def deal_with_pending_sales():

# Create your views here.
def add_share_to_investments_view(request):
    id = request.POST.get('share')
    prices = request.POST.get('prices')
    user_price = request.POST.get('price')
    share = Share.objects.get(id=id)
    num_shares = int(request.POST.get('num_shares', 0))
    initial_shares = num_shares

    # allow shares to be bought correctly
    valid_sales = PendingSale.objects.filter(inv_share__share__id=id).filter(salePrice__lte=user_price) # fix so no one underpays on shares
    sum = valid_sales.aggregate(sum=Sum('numShares'))['sum']

    if not sum or num_shares > sum:
        # use sessions framework to let user know error occured
        # look up how error could be handled
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    while num_shares > 0:
        curr_price = valid_sales.aggregate(Min('salePrice'))['salePrice__min']
        curr_sales = valid_sales.filter(salePrice=curr_price)
        curr_sales = curr_sales.order_by('created')

        for sale in curr_sales:
            ball_street = False
            if sale.seller.username == 'BallStreet':
                ball_street = True
                ball_share = Share.objects.get(id=id)
            if num_shares == 0:
                break

            elif num_shares >= sale.numShares:
                Request.objects.createRequest(
                    sale.seller,
                    request.user.profile,
                    sale.numShares,
                    sale.salePrice,
                    sale.inv_share
                )

                num_shares -= sale.numShares
                sale.delete()
            else:
                Request.objects.createRequest(
                    sale.seller,
                    request.user.profile,
                    num_shares,
                    sale.salePrice,
                    sale.inv_share
                )

                sale.numShares -= num_shares
                sale.save()
                num_shares = 0

    return render(request, 'success/invest_success.html')

def game_success_view(request):
    if request.method == 'POST':
        id = request.POST.get('game_id')
        amount = float(request.POST.get('amount'))
        game = Game.objects.get(id=id)
        bet = request.POST.get('bet')

        amOdds = 0
        odds = 0
        if bet == '1':
            amOdds = game.homeML
            odds = game.homeOdds
        elif bet == '2':
            amOdds = game.awayML
            odds = game.awayOdds
        else:
            amOdds = -110
            odds = game.spreadOdds

        riskOrWin = request.POST.get('riskOrWin')
        if riskOrWin == 'risk':
            if amount > float(request.POST.get('maxRisk')):
                return redirect('/games/')

            inv_share = InvestedGame.objects.createInvestment(
                request.user,
                game,
                abs(round(amount, 2)),
                amOdds,
                odds,
                int(bet)
            )
        elif riskOrWin == 'win':
            if amount > game.maxToWin:
                return redirect('/games/')

            amount = (amount / (odds-1))

            inv_share = InvestedGame.objects.createInvestment(
                request.user,
                game,
                abs(round(amount, 2)),
                amOdds,
                odds,
                int(bet)
            )

        context = {}
        return render(request, 'success/game_success.html', context)
