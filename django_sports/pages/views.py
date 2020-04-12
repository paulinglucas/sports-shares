from django.shortcuts import render
from shares.models import Share, Game
from held_shares.models import InvestedShare, InvestedGame
from exchanges.models import Request
from decimal import Decimal

def checkIfBetsWon():
	for share in InvestedShare.objects.all():
		if share.share.done == True:
			share.hidden = True
			share.save()
		if share.share.win == True:
			share.user.profile.current_profit += Decimal(share.numSharesHeld*10)
			share.user.profile.save()
			share.hidden = True
			share.save()
			for share in Share.objects.all():
				share.hidden = True
				share.save()

def checkIfGamesWon():
	for share in InvestedGame.objects.all():
		if (share.game.gameOver == False) and (share.game.didHomeWin or share.game.didAwayWin or share.game.didHomeSpread or share.game.didAwaySpread):
			if share.game.didHomeWin and share.bet == 1:
				share.user.profile.current_profit += round(Decimal(share.oddsAtPurchase)*share.amountUsed, 2)
			if share.game.didAwayWin and share.bet == 2:
				share.user.profile.current_profit += round(Decimal(share.oddsAtPurchase)*share.amountUsed, 2)
			if share.game.didHomeSpread and share.bet == 3:
				share.user.profile.current_profit += round(Decimal(share.oddsAtPurchase)*share.amountUsed, 2)
			if share.game.didAwaySpread and share.bet == 4:
				share.user.profile.current_profit += round(Decimal(share.oddsAtPurchase)*share.amountUsed, 2)
			share.user.profile.save()
			share.gameOver = True
			share.save()

def home_view(request):
	for s in Share.objects.filter(hidden=True):
		if s.initialAmount > 0 and s.done == False:
			s.hidden = False
			s.save()
	shares = Share.objects.exclude(hidden=True)
	active_seeds = []
	checkIfBetsWon()
	checkIfGamesWon()

	for share in shares:
		if not any(element[0] == share.seed for element in active_seeds):
			element = (share.seed, Share.objects.filter(seed=share.seed).exclude(hidden=True))
			active_seeds.append(element)
	active_seeds = sorted(active_seeds, key=lambda x: x[0])

	context = {
		'shares': shares,
		'seeds': active_seeds
	}
	return render(request, 'index.html', context)

def my_shares_view(request):
	if not request.user.is_anonymous:
		current_profit = request.user.profile.current_profit
		shares = InvestedShare.objects.filter(user=request.user).exclude(hidden=True)
		game_shares = InvestedGame.objects.filter(user=request.user) #.exclude(game.gameOver=True)
		my_requests = Request.objects.exclude(sender=request.user.profile)
		my_sells = Request.objects.filter(sender=request.user.profile)

	context = {
		'profit': current_profit,
		'my_shares': shares,
		'game_shares': game_shares,
		'my_requests': my_requests,
		'my_sells': my_sells
	}
	return render(request, 'my_shares.html', context)


def games_view(request):
	games = Game.objects.exclude(gameStarted=True)
	context = {
		'games': games
	}
	return render(request, 'games.html', context)
