import uuid
from django.db import models
from django.contrib.auth.models import User
import bleach


class Test(models.Model):
    models.AutoField(primary_key=True)
    difficulty = models.CharField(max_length=50)


class Articles(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default='')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', default='')
    date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50)
    test = models.ForeignKey(Test, on_delete=models.SET_NULL, null=True, blank=True)
    total_views = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Sections(models.Model):
    ARTICLE_PART_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(Articles, on_delete=models.CASCADE, related_name='sections')
    part_type = models.CharField(max_length=10, choices=ARTICLE_PART_TYPES)
    text = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='article_images/', null=True, blank=True)
    video_url = models.URLField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    position = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.article.name} - {self.part_type} - {self.position}"

    def save(self, *args, **kwargs):
        if self.text:
            self.text = bleach.clean(self.text, tags=['b', 'i', 'u', 'em', 'strong', 'a', 'ul', 'ol', 'li', 'br'],
                                     attributes={'a': ['href']})
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['position']


class AuthorOfArticle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default='')


class Question(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()

    def __str__(self):
        return self.content


class QuestionInTest(models.Model):
    id = models.AutoField(primary_key=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)


class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    result = models.BooleanField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, default='')


class CustomUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    contribution = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='avatar_images/', null=True, blank=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
