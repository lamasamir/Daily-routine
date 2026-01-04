# tasks/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Task(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['date', 'created_at']




class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    date = models.DateField()
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    class Meta:
        ordering = ['date', 'created_at']
        unique_together = ['user', 'title', 'date']