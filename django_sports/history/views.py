from django.shortcuts import render
from held_shares.models import InvestedGame, InvestedShare
from odds_update.views import calculateProfit
from exchanges.models import Request
from django.contrib.auth.models import User

# Create your views here.
def getUserHistory(user):
    context = {}
    context['profit'] = calculateProfit(user)
    inv_shares = InvestedShare.objects.filter(user=user)
    inv_games = InvestedGame.objects.filter(user=user)
    sell_requests = Request.objects.filter(sender=user.profile)
    buy_requests = Request.objects.filter(receiver=user.profile)

    # shares pending
    shares_pending = inv_shares.filter(hidden=False)
    context['shares_pending'] = shares_pending

    # games pending
    games_pending = inv_games.filter(hidden=False)
    context['games_pending'] = games_pending

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

    # games done
    games_over = inv_games.filter(hidden=True)
    context['games_over'] = games_over

    return context

def user_history_view(request):
    profit = 0
    for user in User.objects.all():
        profit -= user.profile.current_profit
    context = {
        'users': User.objects.all(),
        'profit': profit
    }
    return render(request, 'user_history.html', context)

def user_view(request):
    userid = request.POST.get('user_id')
    user = User.objects.get(id=userid)

    context = getUserHistory(user)
    return render(request, 'shares/user/user.html', context)
