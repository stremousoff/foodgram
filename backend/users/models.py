from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class FoodGramUser(AbstractUser):
    avatar = models.ImageField(upload_to='users/', null=True, blank=True)
