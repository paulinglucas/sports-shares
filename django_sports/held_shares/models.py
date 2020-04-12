from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from shares.models import Share, Game

class InvestedShareManager(models.Manager):
    def createInvestment(self, user, share, numSharesHeld, boughtAt):
        share = self.create(user=user, share=share,
            numSharesHeld=numSharesHeld, boughtAt=boughtAt)
        return share

class InvestedGameManager(models.Manager):
    def createInvestment(self, user, game, amountUsed, amOdds, oddsAtPurchase, bet):
        share = self.create(user=user, game=game,
            amountUsed=amountUsed, amOdds=amOdds, oddsAtPurchase=oddsAtPurchase, bet=bet)
        return share

# Create your models here.
class InvestedShare(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    share = models.ForeignKey(Share, on_delete=models.CASCADE)
    numSharesHeld = models.IntegerField()
    boughtAt = models.CharField(max_length=100, blank=True)
    hidden = models.BooleanField(default=False, editable=False)

    objects = InvestedShareManager()

    def __str__(self):
        return self.user.profile.first_name + " holds " + str(self.numSharesHeld) + " shares in " + self.share.name

class InvestedGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    amountUsed = models.DecimalField(max_digits=10000, decimal_places=2)
    amOdds = models.IntegerField()
    oddsAtPurchase = models.FloatField()
    # 1=homeML, 2=awayML, 3=homeSpread, 4=awaySpread
    bet = models.IntegerField()
    hidden = models.BooleanField(default=False, editable=False)

    objects = InvestedGameManager()

    def __str__(self):
        return self.user.profile.first_name + " bet " + str(self.amountUsed) + " on " + self.game.home + " vs " + self.game.away
