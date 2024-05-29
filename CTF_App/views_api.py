"""
Description:
    This file contains views for the API.
    It uses Django Rest Framework to create API views for the models.
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F
from django.forms import inlineformset_factory, modelformset_factory
from django.http import JsonResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions
from rest_framework import serializers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView

from .models import *
from .serializers import *


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Articles.objects.all()
    serializer_class = ArticleSerializer

    # Trả về tên của tác giả khi truy vấn
    def list(self, request, *args, **kwargs):
        queryset = Articles.objects.all()
        serializer = ArticleSerializer(queryset, many=True)
        for article in serializer.data:
            article['author'] = User.objects.get(id=article['author']).username
        return Response(serializer.data)


class SectionViewSet(viewsets.ModelViewSet):
    serializer_class = SectionSerializer

    # Add id tác giả vào data trả về
    def get_queryset(self):
        """
        Optionally restricts the returned sections,
        by filtering against a `article_id` query parameter in the URL.
        """
        queryset = Sections.objects.all()
        article_id = self.request.query_params.get('article_id', None)
        if article_id is not None:
            queryset = queryset.filter(article=article_id)
        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestDetailSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class QuestionInTestViewSet(viewsets.ModelViewSet):
    queryset = QuestionInTest.objects.all()
    serializer_class = QuestionInTestSerializer


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def update_all_ranks(self):
        """
        Update the ranks of all users based on their score.
        """
        users = CustomUser.objects.all().order_by('-score')
        for index, user in enumerate(users):
            user.rank = index + 1  # Rank starts from 1
            user.save()

    def list(self, request, *args, **kwargs):
        """
        Override the list method to update ranks before returning the list of users.
        """
        self.update_all_ranks()  # Update ranks before listing users
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        """
        Optionally restricts the returned users,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = CustomUser.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(user__username=username)
        return queryset


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, data):
        print(data)

        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(" Username or Email already exists!")

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(" Username or Email already exists!")

        return data

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        user.set_password(validated_data['password'])
        user.save()

        custom_user = CustomUser.objects.create(
            user=user,
            score=0,
            contribution=0,
            rank=0,
            avatar='default.jpg'
        )
        custom_user.save()

        return user


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(generics.GenericAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.Serializer

    def post(self, request, *args, **kwargs):
        from rest_framework.authtoken.models import Token
        from django.contrib.auth import authenticate

        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.pk, 'username': user.username, 'email': user.email})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class CreatemoduleSerializers(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields = ['id', 'name', 'category', 'author']

    def validate(self, data):
        print(data)
        valid_categories = ['Web Security', 'Cryptography', 'Reverse Engineering', 'Forensics', 'Binary Exploitation',
                            'Misc']
        if data['category'] not in valid_categories:
            raise serializers.ValidationError("Invalid category")
        return data

    def create(self, validated_data):
        print(validated_data['author'])
        user = User.objects.get(id=validated_data['author'].id)
        article = Articles.objects.create(
            name=validated_data['name'],
            category=validated_data['category'],
            author=user
        )
        Section = Sections.objects.create(
            article=article,
            part_type='text',
            text='This is a new article. Please add more sections to it.',
            position=1,
        )
        article.save()
        Section.save()
        return article


@method_decorator(csrf_exempt, name='dispatch')
class CreatemoduleView(generics.CreateAPIView):
    queryset = Articles.objects.all()
    serializer_class = CreatemoduleSerializers
    permission_classes = [permissions.AllowAny]


class EmailUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = EmailUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'email updated'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response({'status': 'password updated'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, test_id):
        test = get_object_or_404(Test, id=test_id)
        serializer = TestDetailSerializer(test)
        return Response(serializer.data, status=status.HTTP_200_OK)
