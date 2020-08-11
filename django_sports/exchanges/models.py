from django.db import models
from held_shares.models import InvestedShare
from login.models import Profile
import datetime
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver

class PendingSaleManager(models.Manager):
    def createSale(self, user, price, numShares, inv_share):
        req = self.create(seller=user, numShares=numShares,
        salePrice=price, inv_share=inv_share)
        return req

class RequestManager(models.Manager):
    def createRequest(self, user, buyer, numShares, price, inv_share):
        req = self.create(sender=user, receiver=buyer,
         numShares=numShares, salePrice=price, inv_share=inv_share)
        return req

class PendingSale(models.Model):
    seller = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    salePrice = models.DecimalField("Selling Price", max_digits=10000, decimal_places=2)
    inv_share = models.ForeignKey(InvestedShare, on_delete=models.CASCADE)
    numShares = models.IntegerField("Number of Shares")
    created = models.DateTimeField(default=now, null=True)

    objects = PendingSaleManager()

    def __str__(self):
        return (self.seller.first_name + " selling " + str(self.numShares) +
            " shares of " + self.inv_share.share.name)

class Request(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='request_sender', null=True)
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='request_receiver', null=True)
    inv_share = models.ForeignKey(InvestedShare, on_delete=models.CASCADE)
    numShares = models.IntegerField("Number of Shares Sold")
    salePrice = models.DecimalField("Sale Price", max_digits=10000, decimal_places=2, default=-1.00)
    created = models.DateTimeField(default=now, null=True)

    objects = RequestManager()

    def total_price(self):
        return round(self.salePrice*self.numShares, 2)

    def __str__(self):
        receiverName = ""
        if not self.receiver:
            receiverName = "_______"
        receiverName = self.receiver.first_name
        return (self.sender.first_name + " sells " + str(self.numShares) +
            " shares of " + self.inv_share.share.name + " to " + receiverName)
