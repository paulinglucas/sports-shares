from django.db import models
from django.utils.timezone import now
from login.models import Profile

# Create your models here.
class Payment(models.Model):
    payer = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    amount_paid = models.CharField("Amount Paid", max_length=100)
    created = models.DateTimeField(default=now, null=True)

    def __str__(self):
        return str(self.payer) + " paid $" + self.amount_paid

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.amount_paid = self.amount_paid.replace("$", "")
        super().save(*args, **kwargs)
