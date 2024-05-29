from rest_framework import serializers
from .models import *


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields = ['id', 'name', 'author', 'date', 'category', 'test', 'total_views']


class SectionSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source='article.author.id', read_only=True)

    class Meta:
        model = Sections
        fields = ['id', 'article', 'part_type', 'text', 'image', 'video_url', 'created_at', 'position', 'author_id']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'article', 'text', 'created_at']


class TestDetailSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = ['id', 'difficulty', 'questions']

    def get_questions(self, obj):
        questions_in_test = QuestionInTest.objects.filter(test=obj)
        questions = [question_in_test.question for question_in_test in questions_in_test]
        return QuestionSerializer(questions, many=True).data


class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'content', 'answers']

    def get_answers(self, obj):
        answers = Answer.objects.filter(question=obj)
        return AnswerSerializer(answers, many=True).data



class QuestionInTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionInTest
        fields = ['id', 'test', 'question']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'content', 'result']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class CustomUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'user', 'score', 'contribution', 'rank', 'avatar']


class EmailUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect old password.")
        return value

    def validate(self, data):
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        if old_password == new_password:
            raise serializers.ValidationError("New password must be different from old password.")
        return data
