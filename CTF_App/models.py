from django.db import models
from django.contrib.auth.models import AbstractUser


class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author_id = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    test_id = models.CharField(max_length=100, default="")
    category = models.TextField(default="General")

    def __str__(self):
        return self.title
