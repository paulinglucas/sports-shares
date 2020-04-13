from django.db import models
from held_shares.models import InvestedShare
from login.models import Profile

# Create your models here.
class RequestManager(models.Manager):
    def createRequest(self, user, numShares, inv_share):
        req = self.create(sender=user,
         numShares=numShares, inv_share=inv_share)
        return req


class Request(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='request_sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='request_receiver', blank=True, null=True)
    inv_share = models.ForeignKey(InvestedShare, on_delete=models.CASCADE)
    numShares = models.IntegerField()
    salePrice = models.DecimalField(max_digits=10000, decimal_places=2, default=-1.00)
    hidden = models.BooleanField(default=False)

    objects = RequestManager()

    def __str__(self):
        return "Request " + str(id)
