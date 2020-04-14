from django.shortcuts import render, redirect
from shares.models import Share, Game
from held_shares.models import InvestedShare, InvestedShareManager, InvestedGame
from decimal import Decimal

# Create your views here.
def add_share_to_investments_view(request):
    id = request.POST.get('share')
    share = Share.objects.get(id=id)
    num_shares = int(request.POST.get('num_shares', 0))
    if num_shares > share.initialAmount:
        return redirect('/')
    share.initialAmount -= num_shares
    share.save()

    inv_share = InvestedShare.objects.createInvestment(
        request.user,
        share,
        num_shares,
        share.pricePerShare
    )
    # request.user.profile.current_profit -= Decimal(round(num_shares*float(share.pricePerShare), 2))
    # request.user.profile.save()

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
                round(amount, 2),
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
                round(amount, 2),
                amOdds,
                odds,
                int(bet)
            )

        context = {}
        return render(request, 'success/game_success.html', context)
