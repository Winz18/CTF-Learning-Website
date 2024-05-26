from rest_framework import serializers
from .models import Articles, Sections, Comment, Test, Question, QuestionInTest, Answer, CustomUser

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields = ['id', 'name', 'author', 'date', 'category', 'test', 'total_views']

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sections
        fields = ['id', 'article', 'part_type', 'text', 'image', 'video_url', 'created_at', 'position']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'article', 'text', 'created_at']

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'difficulty']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'content']

class QuestionInTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionInTest
        fields = ['id', 'test', 'question']

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'content', 'result', 'question']

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'user', 'score', 'contribution', 'rank', 'avatar']
