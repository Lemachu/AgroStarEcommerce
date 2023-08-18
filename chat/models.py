from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account
# Create your models here.


class ChatModel(models.Model):
    sender = models.CharField(max_length=100, default=None)
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE, default=None)
    message = models.TextField(null=True, blank=True)
    thread_name = models.CharField(null=True, blank=True, max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.message