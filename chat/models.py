from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    title=models.CharField(max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
class Message(models.Model):
    class Role(models.TextChoices):
        USER="user", "User"
        AI="ai", "Ai"
    role=models.CharField(max_length=10, choices=Role.choices)
    content=models.TextField()
    conversation=models.ForeignKey(Conversation, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)