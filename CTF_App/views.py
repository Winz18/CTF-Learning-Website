from django.db.models import F
from django.views import generic
from django.shortcuts import get_object_or_404
from .models import Articles, CustomUser
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse


class IndexView(generic.ListView):
    template_name = "CTF_App/index.html"
    context_object_name = "latest_article_list"
    model = Articles

    def get_queryset(self):
        return Articles.objects.order_by(F("date").desc())


class DetailView(generic.DetailView):
    template_name = "CTF_App/article_detail.html"
    model = Articles
    context_object_name = "article"

    def get_object(self):
        # Lấy đối tượng bài viết dựa trên id của nó
        return get_object_or_404(Articles, id=self.kwargs['pk'])


class ScoreboardView(generic.ListView):
    template_name = 'CTF_App/scoreboard.html'
    context_object_name = 'users'
    model = User

    def get_queryset(self):
        return User.objects.annotate(score=F('customuser__score')).select_related('customuser').order_by(
            F('customuser__score').desc(), 'date_joined')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect('CTF_App:index')
        else:
            # Return an 'invalid login' error message.
            return render(request, "CTF_App/index.html", {'error_message': 'Invalid login'})
    else:
        return render(request, 'CTF_App/login.html')


def user_logout(request):
    logout(request)
    # Redirect to a success page.
    return redirect('CTF_App:index')


def user_signup(request):
    if request.method == 'POST':
        # Lấy dữ liệu từ form đăng ký
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        # Tạo một user mới
        user = User.objects.create_user(username=username, password=password, email=email)

        # Lưu user mới vào cơ sở dữ liệu
        user.save()

        # Đăng nhập người dùng sau khi đăng ký (tuỳ chọn)
        # authenticate và login giúp đăng nhập người dùng sau khi họ đăng ký
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

        # Chuyển hướng người dùng đến trang chủ hoặc trang sau khi đăng ký thành công
        return redirect('CTF_App:index')

    # Nếu không phải là phương thức POST, render template cho trang đăng ký
    return render(request, 'CTF_App/signup.html')
