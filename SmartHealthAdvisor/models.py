from django.db import models
from django.db import models
from django.contrib.auth.models import User

class UserHealthStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    heart_rate = models.IntegerField(default=72)
    spo2 = models.IntegerField(default=98)
    steps = models.IntegerField(default=5000)
    sleep_hours = models.FloatField(default=7.5)
    
    # We can also store the Prakriti result here if you want
    prakriti_type = models.CharField(max_length=50, default="Unknown")

    def __str__(self):
        return f"{self.user.username}'s Stats"
# Create your models here.
