from django.db.models import F
from django.views import generic
from django.shortcuts import get_object_or_404
from .models import Articles, CustomUser
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib import messages


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


@login_required
def profile_view(request):
    user = request.user
    context = {
        'user': user,
        # Truy vấn các thông tin khác của người dùng từ database và truyền vào context
    }
    return render(request, 'CTF_App/profile.html', context)


class ChangeUsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']


class ChangeEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label='Old Password')
    new_password = forms.CharField(widget=forms.PasswordInput, label='New Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm New Password')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError("New password and confirm password do not match.")


@login_required
def change_username(request):
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your username was successfully updated!')
            return redirect('CTF_App:profile')
    else:
        form = ChangeUsernameForm(instance=request.user)
    return render(request, 'CTF_App/change_username.html', {'form': form})


@login_required
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your email was successfully updated!')
            return redirect('CTF_App:profile')
    else:
        form = ChangeEmailForm(instance=request.user)
    return render(request, 'CTF_App/change_email.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data.get('old_password')
            new_password = form.cleaned_data.get('new_password')
            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)  # Important!
                messages.success(request, 'Your password was successfully updated!')
                return redirect('CTF_App:profile')
            else:
                messages.error(request, 'Old password is incorrect.')
    else:
        form = ChangePasswordForm()
    return render(request, 'CTF_App/change_password.html', {'form': form})
