from django.shortcuts import render
from shares.models import Share, Event, Category, Game
from held_shares.models import InvestedShare, InvestedGame
from exchanges.models import Request, PendingSale
from decimal import Decimal
from odds_update.views import calculateProfit

def checkIfGamesWon():
	for game in Game.objects.exclude(gameOver=True):
		if (game.gameOver == False) and (game.didHomeWin or game.didAwayWin or game.didHomeSpread or game.didAwaySpread):
			game.gameOver = True
			game.save()
	for game in InvestedGame.objects.exclude(hidden=True):
		if game.game.gameOver:
			game.hidden = True
			game.save()

def home_view(request):
	shares = Share.objects.exclude(done=True)
	active_seeds = []
	checkIfGamesWon()
	return render(request, 'index.html')

def my_shares_view(request):
	if not request.user.is_anonymous:
		calculateProfit(request.user.profile)
		current_profit = request.user.profile.current_profit
		shares = InvestedShare.objects.filter(user=request.user.profile).exclude(hidden=True)
		game_shares = InvestedGame.objects.filter(user=request.user).exclude(hidden=True)
		my_sells = PendingSale.objects.filter(seller=request.user.profile)

	context = {
		'user': request.user.profile,
		'profit': current_profit,
		'my_shares': shares,
		'game_shares': game_shares,
		'my_sells': my_sells
	}
	return render(request, 'my_shares.html', context)


def games_view(request):
	games = Game.objects.exclude(gameStarted=True)
	context = {
		'games': games
	}
	return render(request, 'games.html', context)

def user_history_view(request):
	sales = Request.objects.filter(sender=request.user.profile)
	buys = Request.objects.filter(receiver=request.user.profile)
	context = {
		'sales': sales,
		'buys': buys,
		'user': request.user.profile
	}
	return render(request, 'shares/user/history.html', context)

def events_view(request, sport):
	bets = Event.objects.filter(category=Category.objects.get(name=sport))
	print(bets)
	context = {
		'bets': bets,
		'sport': sport
	}
	return render(request, 'events/events.html', context)

def event_view(request, sport, id):
	event = Event.objects.get(id=id)
	people = Share.objects.filter(event=event)

	salesAndShares = []

	for person in people:
		pricesList = []
		if not any(element[0] == person for element in salesAndShares):
			sales = PendingSale.objects.filter(inv_share__share=person) #.order_by('salePrice')[:3]
			if not sales:
				element = (person, pricesList)
				salesAndShares.append(element)
				continue
			prices = {}
			for sale in sales:
				if sale.salePrice in prices:
					prices[sale.salePrice] += sale.numShares
				else: prices[sale.salePrice] = sale.numShares
			lst = list(prices.keys())
			lst.sort()
			person.pricePerShare = lst[0]
			person.save()
			for p in lst:
				pricesList.append((p, prices[p]))

			element = (person, pricesList)
			salesAndShares.append(element)
	# salesAndShares = sorted(active_seeds, key=lambda x: x[0])
	context = {
		'salesAndShares': salesAndShares,
		'event': event
	}
	return render(request, 'events/event-hub.html', context)
