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
        id = request.POST.get('share')
        share = Game.objects.get(id=id)
        amount = Decimal(request.POST.get('amount'))
        odds = None
        amOdds = None
        data = request.POST.copy()
        bet = 0
        if 'homeML' in data:
            bet = 1
            amOdds = share.homeML
            if amOdds < 0:
                odds = 1 - (100/amOdds)
            else:
                odds = 1 + (amOdds/100)

        elif 'awayML' in data:
            bet = 2
            amOdds = share.awayML
            if amOdds < 0:
                odds = 1 - (100/amOdds)
            else:
                odds = 1 + (amOdds/100)
        else:
            amOdds = -110
            odds = 1 - (100/amOdds)
            if 'homeSpread' in data:
                bet = 3
            else:
                bet = 4

        inv_share = InvestedGame.objects.createInvestment(
            request.user,
            share,
            amount,
            amOdds,
            odds,
            bet
        )

        # request.user.profile.current_profit -= Decimal(amount)
        # request.user.profile.save()

        context = {}
        return render(request, 'success/game_success.html', context)
