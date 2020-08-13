from django.conf import settings
from django.db import models
from decimal import Decimal
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.db.models.signals import post_delete
from exchanges.models import PendingSale
from django.utils.timezone import now
from login.models import Profile
from held_shares.models import InvestedShare
from django.db.models import Min

# category
class Category(models.Model):
    name = models.CharField("Name", max_length=100)

    def __str__(self):
        return self.name

# futures contract
class Event(models.Model):
    name = models.CharField("Event Name", max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    done = models.BooleanField("Outcome decided", default=False)

    def __str__(self):
        return self.name

# Create your models here.
class Share(models.Model):
    name = models.CharField("Name", max_length=100)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    initialAmount = models.IntegerField("Amount of Initial Shares", default=50)
    tradedAmount = models.IntegerField("Amount being traded", editable=False, default=0)
    americanOdds = models.IntegerField("Odds")
    recommendedPrice = models.CharField("Price/Share", max_length=100, blank=True, editable=False)
    lastSoldPrice = models.CharField("Last Sold at", max_length=100, blank=True, editable=False, default="0.00")
    hidden = models.BooleanField("Hide", default=False)
    done = models.BooleanField("No longer viable", default=False)
    win = models.BooleanField("Winner", default=False)
    created = models.DateTimeField(default=now, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oldOdds = self.americanOdds

    def __str__(self):
        return self.name

    def amount(self):
        return self.initialAmount + self.tradedAmount

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
            return "{:.2f}".format(round(pps, 2))
        elif odds < 0:
            pps = (-1*odds / (-1*odds + 100))*10
            return "{:.2f}".format(round(pps, 2))
        else:
            return "5.00"

    def getOdds(self, pps):
        if pps == None:
            return 0
        if pps == 10:
            return -100000
        pps = float(pps) * 10
        if pps > 50:
            return round((pps / (1 - (pps/100))) * -1)
        if pps == 50:
            return 100
        else:
            return round((100 / (pps / 100)) - 100)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.amount() > 0:
            sales = PendingSale.objects.filter(inv_share__share__id=self.id)
            lowest_sale = sales.aggregate(Min('salePrice'))['salePrice__min']
            self.americanOdds = self.getOdds(lowest_sale)

        if self.done or self.win:
            self.hidden = True
        if not self.recommendedPrice:
            self.recommendedPrice = self.getPPS(self.americanOdds)
        if self.oldOdds != self.americanOdds:
            self.recommendedPrice = self.getPPS(self.americanOdds)
            self.oldOdds = self.americanOdds
            self.save()
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.oldHomeML = self.homeML
        self.oldAwayML = self.awayML
        self.oldHomeOdds = self.homeOdds
        self.oldAwayOdds = self.awayOdds

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
        return round((self.maxToWin / Decimal(odds-1)), 2)

    def __str__(self):
        return self.home + " vs " + self.away

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if not self.homeOdds:
            self.homeOdds = self.convertOdds(self.homeML)
        elif self.oldHomeML != self.homeML:
            self.homeOdds = self.convertOdds(self.homeML)
            self.oldHomeML = self.homeML

        if not self.awayOdds:
            self.awayOdds = self.convertOdds(self.awayML)
        elif self.oldAwayML != self.awayML:
            self.awayOdds = self.convertOdds(self.awayML)
            self.oldAwayML = self.awayML

        if not self.maxToRiskHome:
            self.maxToRiskHome = round(self.findMaxToRisk(self.homeOdds), 2)
        elif self.oldHomeOdds != self.homeOdds:
            self.maxToRiskHome = round(self.findMaxToRisk(self.homeOdds), 2)
            self.oldHomeOdds = self.homeOdds
            self.oldMaxHome = self.maxToRiskHome

        if not self.maxToRiskAway:
            self.maxToRiskAway = round(self.findMaxToRisk(self.awayOdds), 2)
        elif self.oldAwayOdds != self.awayOdds:
            self.maxToRiskAway = round(self.findMaxToRisk(self.awayOdds), 2)
            self.oldAwayOdds = self.awayOdds
            self.oldMaxAway = self.maxToRiskAway

        if not self.maxToRiskSpread:
            self.maxToRiskSpread = round(self.findMaxToRisk(self.spreadOdds), 2)
        super().save(*args, **kwargs)

@receiver(post_save, sender=PendingSale)
def update_share_signal(sender, instance, created, **kwargs):
    share = Share.objects.get(id=instance.inv_share.share.id)
    if created and instance.seller.user.username != 'BallStreet':
        share.tradedAmount += instance.numShares
        share.save()
        instance.inv_share.numSharesHeld -= instance.numShares
        instance.inv_share.save()

@receiver(pre_delete, sender=PendingSale)
def update_inv_share_signal(sender, instance, **kwargs):
    instance.inv_share.numSharesHeld += instance.numShares
    instance.inv_share.save()
    share = Share.objects.get(id=instance.inv_share.share.id)
    share.tradedAmount -= instance.numShares
    share.save()

@receiver(post_delete, sender=PendingSale)
def update_price(sender, instance, **kwargs):
    sales = PendingSale.objects.all()
    share = Share.objects.get(id=instance.inv_share.share.id)
    lowest_sale = sales.aggregate(Min('salePrice'))['salePrice__min']
    share.americanOdds = share.getOdds(lowest_sale)
    share.save()

## TODO: Fix update in sale price for bllastreet pending sale according to changes
@receiver(post_save, sender='shares.Share')
def update_sale_signal(sender, instance, created, **kwargs):
    if created:
        site_user = Profile.objects.get(user__username='BallStreet')
        inv_share = InvestedShare.objects.createInvestment(
            user=site_user,
            share=instance,
            numSharesHeld=instance.initialAmount,
        )
        PendingSale.objects.create(
            seller=site_user,
            salePrice=instance.recommendedPrice,
            inv_share=inv_share,
            numShares=instance.initialAmount
        )
    else:
        try:
            sale = PendingSale.objects.filter(inv_share__share__id=instance.id).get(seller__username='BallStreet')
            sale.inv_share.numSharesHeld = instance.initialAmount
            sale.inv_share.save()
            sale.numShares = instance.initialAmount

            if sale.salePrice < Decimal(instance.recommendedPrice):
                sale.salePrice = Decimal(instance.recommendedPrice)
            sale.save()
        except PendingSale.DoesNotExist:
            pass

        if instance.done == True or instance.win == True:

            for share in InvestedShare.objects.filter(share=instance):
                share.hidden = True
                share.save()

            for req in PendingSale.objects.filter(inv_share__share=instance):
                req.delete()

        if not instance.hidden:
            for share in InvestedShare.objects.filter(share=instance):
                if share.numSharesHeld > 0:
                    share.hidden = False
                    share.save()

            for req in PendingSale.objects.filter(inv_share__share=instance):
                req.hidden = False
                req.save()

@receiver(post_save, sender='exchanges.Request')
def update_share_signal2(sender, instance, created, **kwargs):
    share = Share.objects.get(id=instance.inv_share.share.id)
    if created:
        if instance.sender.user.username != 'BallStreet':
            share = Share.objects.get(id=instance.inv_share.share.id)
            share.tradedAmount -= instance.numShares

        elif instance.sender.user.username == 'BallStreet':
            share.initialAmount -= instance.numShares

        seller_share = InvestedShare.objects.filter(share__id=instance.inv_share.share.id).get(user=instance.sender)

        try:
            buyer_share = InvestedShare.objects.filter(share__id=instance.inv_share.share.id).get(user=instance.receiver)
            buyer_share.numSharesHeld += instance.numShares
            buyer_share.save()
        except InvestedShare.DoesNotExist:
            buyer_share = InvestedShare.objects.createInvestment(
                instance.receiver,
                instance.inv_share.share,
                instance.numShares
            )

        seller_share.numSharesHeld -= instance.numShares
        if seller_share.numSharesHeld == 0:
            seller_share.hidden = True
            seller_share.save()
        elif seller_share.numSharesHeld > 0:
            seller_share.save()
        else:
            raise Exception

        share.lastSoldPrice = str(instance.salePrice)
        share.save()
