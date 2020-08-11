from django.shortcuts import render
from held_shares.models import InvestedGame, InvestedShare
from odds_update.views import calculateProfit, calculateTotalShareProfit
from exchanges.models import Request
from django.contrib.auth.models import User
from shares.models import Share, Game
from login.models import Profile

def calculateAllProfits():
    for user in Profile.objects.all().exclude(username='BallStreet'):
        calculateProfit(user)

def findPotentialWinnings(share):
    winnings = 0
    for vested_share in InvestedShare.objects.filter(share=share).exclude(user__username='BallStreet'):
        winnings += vested_share.numSharesHeld*10
    return winnings

# Create your views here.
def getUserHistory(user):
    context = {}
    context['profit'] = calculateProfit(user)
    inv_shares = InvestedShare.objects.filter(user=user)
    inv_games = InvestedGame.objects.filter(user=user)
    sell_requests = Request.objects.filter(sender=user.profile)
    buy_requests = Request.objects.filter(receiver=user.profile)

    # games pending
    games_pending = inv_games.filter(hidden=False)
    context['games_pending'] = games_pending

    # games done
    games_over = inv_games.filter(hidden=True)
    context['games_over'] = games_over

    # shares pending
    shares_pending = inv_shares.filter(hidden=False)
    context['shares_pending'] = shares_pending

    # sell requests pending
    sales_pending = sell_requests.filter(hidden=False)
    context['sales_pending'] = sales_pending

    # sold requests
    sales = sell_requests.filter(hidden=True)
    context['sales'] = sales

    # bought requests
    buys = buy_requests.filter(hidden=True)
    context['buys'] = buys

    # shares done
    shares_done = inv_shares.filter(hidden=True)
    context['shares_done'] = shares_done

    return context

def user_history_view(request):
    calculateAllProfits()
    profit = 0
    for user in User.objects.all():
        profit -= user.profile.current_profit

    shares = []
    for s in Share.objects.filter(done=False):
        shares.append((s, findPotentialWinnings(s)))
    shares.sort(key = lambda x: x[1])
    shares.reverse()
    if len(shares) >= 5:
        shares = shares[:5]
    else:
        shares = shares[:len(shares)]

    shareProfit = round(calculateTotalShareProfit(), 2)

    top5users = Profile.objects.order_by('-current_profit')[:5]

    context = {
        'users': User.objects.all(),
        'profit': profit,
        'shares': shares,
        'top5': top5users,
        'shareProfit': shareProfit
    }
    return render(request, 'user_history.html', context)

def user_view(request):
    userid = request.POST.get('user_id')
    user = User.objects.get(id=userid)

    context = getUserHistory(user)
    return render(request, 'shares/user/user.html', context)
