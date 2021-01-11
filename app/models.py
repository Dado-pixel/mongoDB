from django.db import models
from djongo.models.fields import ObjectIdField
from django.contrib.auth.models import User
from django.conf import settings

class Profile(models.Model):
    _id = ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.FloatField()
    
class Order(models.Model):
    _id = ObjectIdField()
    profile = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    buy = models.BooleanField(blank=True)
    sell = models.BooleanField(blank=True)
    price = models.FloatField()
    quantity = models.FloatField()
    execute = models.BooleanField(blank=True, default=False)
    profit = models.FloatField(default=0)
