from django.conf import settings
from django.db import models

# Create your models here.
class Share(models.Model):
    name = models.CharField(max_length=100)
    seed = models.IntegerField()
    initialAmount = models.IntegerField(default=50)
    americanOdds = models.IntegerField()
    pricePerShare = models.CharField(max_length=100, blank=True, editable=False)
    hidden = models.BooleanField(default=False, editable=False)
    done = models.BooleanField(default=False)
    win = models.BooleanField(default=False)
    # moneyInvested = models.FloatField()
    # moneyToWin = models.FloatField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oldOdds = self.americanOdds

    def __str__(self):
        return self.name

    def convertOddsToStr(self):
        if self.americanOdds > 0:
            return "+" + str(self.americanOdds)
        elif self.americanOdds == 0:
            return "EVEN"
        else:
            return str(self.americanOdds)

    def getPPS(self, odds):
        if odds > 0:
            pps = (100 / (odds + 100))*10
            return str(round(pps, 2))
        elif odds < 0:
            pps = (-1*odds / (-1*odds + 100))*10
            return str(round(pps, 2))
        else:
            return "5.00"

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.done:
            self.hidden = True
        if not self.pricePerShare:
            self.pricePerShare = self.getPPS(self.americanOdds)
        if self.oldOdds != self.americanOdds:
            self.pricePerShare = self.getPPS(self.americanOdds)
        self.oldOdds = self.americanOdds
        super().save(*args, **kwargs)

class Game(models.Model):
    home = models.CharField(max_length=100)
    away = models.CharField(max_length=100)
    homeML = models.IntegerField()
    awayML = models.IntegerField()
    homeSpread = models.DecimalField(max_digits=10, decimal_places=1)
    awaySpread = models.DecimalField(max_digits=10, decimal_places=1)
    didHomeWin = models.BooleanField(default=False)
    didHomeSpread = models.BooleanField(default=False)
    didAwayWin = models.BooleanField(default=False)
    didAwaySpread = models.BooleanField(default=False)
    # maxToRisk = models.DecimalField(max_digits=10000, decimal_places=2, blank=True)
    maxToWin = models.DecimalField(max_digits=10000, decimal_places=2, default=100)
    gameStarted = models.BooleanField(default=False)
    gameOver = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return self.home + " vs " + self.away
