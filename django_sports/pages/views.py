from django.shortcuts import render
from shares.models import Share, Game
from held_shares.models import InvestedShare, InvestedGame
from exchanges.models import Request
from decimal import Decimal

def checkIfBetsWon():
	shares_to_delete = []
	for share in InvestedShare.objects.all():
		if share.share.win == True:
			share.user.profile.current_profit += Decimal(share.numSharesHeld*10)
			share.user.profile.save()
			if share.share not in shares_to_delete:
				shares_to_delete.append(share.share)
			share.delete()
	for share in shares_to_delete:
		share.delete()

def checkIfGamesWon():
	shares_to_delete = []
	for share in InvestedGame.objects.all():
		if share.game.didHomeWin or share.game.didAwayWin or share.game.didHomeSpread or share.game.didAwaySpread:
			if share not in shares_to_delete:
				shares_to_delete.append(share.game)
			if share.game.didHomeWin:
				if share.bet == 1:
					share.user.profile.current_profit += round(Decimal(share.oddsAtPurchase)*share.amountUsed, 2)
			if share.game.didAwayWin:
				if share.bet == 2:
					share.user.profile.current_profit += round(Decimal(share.oddsAtPurchase)*share.amountUsed, 2)
			if share.game.didHomeSpread:
				if share.bet == 3:
					share.user.profile.current_profit += round(Decimal(share.oddsAtPurchase)*share.amountUsed, 2)
			if share.game.didAwaySpread:
				if share.bet == 4:
					share.user.profile.current_profit += round(Decimal(share.oddsAtPurchase)*share.amountUsed, 2)
			share.user.profile.save()
			share.delete()

	for share in shares_to_delete:
		share.delete()

def home_view(request):
	shares = Share.objects.all()
	active_seeds = []
	checkIfBetsWon()
	checkIfGamesWon()

	for share in shares:
		if not any(element[0] == share.seed for element in active_seeds):
			element = (share.seed, Share.objects.filter(seed=share.seed))
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
		shares = InvestedShare.objects.filter(user=request.user)
		game_shares = InvestedGame.objects.filter(user=request.user)
		my_requests = Request.objects.filter(receiver=request.user.profile)

	context = {
		'profit': current_profit,
		'my_shares': shares,
		'game_shares': game_shares,
		'my_requests': my_requests
	}
	return render(request, 'my_shares.html', context)


def games_view(request):
	games = Game.objects.all()
	context = {
		'games': games
	}
	return render(request, 'games.html', context)
