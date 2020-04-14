from django.conf import settings
from django.db import models
from decimal import Decimal

# Create your models here.
class Share(models.Model):
    name = models.CharField("Name", max_length=100)
    seed = models.IntegerField("Seed")
    initialAmount = models.IntegerField("Amount of Available Shares", default=50)
    americanOdds = models.IntegerField("Odds")
    pricePerShare = models.CharField("Price/Share", max_length=100, blank=True, editable=False)
    hidden = models.BooleanField("Hide", default=False)
    done = models.BooleanField("Out of Tournament", default=False)
    win = models.BooleanField("Winner", default=False)
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
    home = models.CharField("Home Team", max_length=100)
    away = models.CharField("Away Team", max_length=100)

    homeML = models.IntegerField("Home Moneyline")
    homeOdds = models.FloatField(default=0, editable=False)
    maxToRiskHome = models.DecimalField(max_digits=10, decimal_places=2, null=True, editable=False)

    awayML = models.IntegerField("Away Moneyline")
    awayOdds = models.FloatField(default=0, editable=False)
    maxToRiskAway = models.DecimalField(max_digits=10, decimal_places=2, null=True, editable=False)

    homeSpread = models.DecimalField("Home Spread", max_digits=10, decimal_places=1)
    awaySpread = models.DecimalField("Away Spread", max_digits=10, decimal_places=1)
    spreadOdds = models.FloatField(default=1.91, editable=False)
    maxToRiskSpread = models.DecimalField(max_digits=10, decimal_places=2, null=True, editable=False)

    # maxToRisk = models.DecimalField(max_digits=10000, decimal_places=2, blank=True)
    maxToWin = models.DecimalField("Max Amount to Win", max_digits=10000, decimal_places=2, default=100)
    gameStarted = models.BooleanField("Game has Begun", default=False)
    gameOver = models.BooleanField("Game is Over", default=False, editable=False)

    didHomeWin = models.BooleanField("Home Team Won", default=False)
    didHomeSpread = models.BooleanField("Home Covered Spread", default=False)
    didAwayWin = models.BooleanField("Away Team Won", default=False)
    didAwaySpread = models.BooleanField("Away Covered Spread", default=False)

    def convertOdds(self, odds):
        if odds == self.homeML:
            if odds < 0:
                odds = 1 - (100/odds)
            else:
                odds = 1 + (odds/100)

        elif odds == self.awayML:
            if odds < 0:
                odds = 1 - (100/odds)
            else:
                odds = 1 + (odds/100)
        else:
            odds = -110
            odds = 1 - (100/odds)

        return odds

    def findMaxToRisk(self, odds):
        return round((self.maxToWin / Decimal(odds)), 2)

    def __str__(self):
        return self.home + " vs " + self.away

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if not self.homeOdds:
            self.homeOdds = self.convertOdds(self.homeML)
        if not self.awayOdds:
            self.awayOdds = self.convertOdds(self.awayML)
        if not self.maxToRiskHome:
            self.maxToRiskHome = round(self.findMaxToRisk(self.homeOdds), 2)
        if not self.maxToRiskAway:
            self.maxToRiskAway = round(self.findMaxToRisk(self.awayOdds), 2)
        if not self.maxToRiskSpread:
            self.maxToRiskSpread = round(self.findMaxToRisk(self.spreadOdds), 2)
        super().save(*args, **kwargs)
