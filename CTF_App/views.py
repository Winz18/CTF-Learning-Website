from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from .models import Articles, Sections, Test, QuestionInTest, Question, Answer, Answer_Question, CustomUser
from django.forms import inlineformset_factory


class IndexView(generic.ListView):
    template_name = "CTF_App/index.html"
    context_object_name = "latest_article_list"
    model = Articles

    def get_queryset(self):
        # Lấy chủ đề cần lọc từ request.GET
        category = self.request.GET.get('category')
        search_query = self.request.GET.get('search')

        queryset = Articles.objects.all()

        if category:
            queryset = queryset.filter(category=category)

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset.order_by('-date')[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class DetailView(generic.DetailView):
    template_name = "CTF_App/article_detail.html"
    model = Articles
    context_object_name = "article"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = self.get_object().sections.order_by('position')
        return context


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
            messages.error(request, 'Invalid username or password. Please try again.')
            return render(request, "CTF_App/login.html")
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

        # Tạo một CustomUser mới tương ứng với user mới
        custom_user = CustomUser.objects.create(
            user=user,
            score=0,
            contribution=0,
            rank=0
        )

        # Lưu CustomUser mới vào cơ sở dữ liệu
        custom_user.save()

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
    current_user = request.user
    ordered_users_list = CustomUser.objects.order_by('-score', '-contribution')
    rank = list(ordered_users_list).index(current_user.customuser) + 1
    context = {
        'user': current_user,
        'score': CustomUser.objects.get(user=current_user).score,
        'contribution': CustomUser.objects.get(user=current_user).contribution,
        'rank': rank,
    }
    return render(request, 'CTF_App/profile.html', context)


class ChangeUsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']


class ChangeEmailForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'size': '50'}))

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


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Articles
        fields = ['name', 'category']


class SectionForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = Sections
        fields = ['part_type', 'text', 'image', 'video_url']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 20, 'cols': 80}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
        }


class ArticleCreateView(generic.CreateView):
    model = Articles
    form_class = ArticleForm
    template_name = 'CTF_App/article_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('CTF_App:article_detail', kwargs={'pk': self.object.pk})


@login_required
def add_section(request, article_id):
    article = get_object_or_404(Articles, id=article_id)
    if request.method == 'POST':
        form = SectionForm(request.POST, request.FILES)
        if form.is_valid():
            section = form.save(commit=False)
            section.article = article
            section.save()
            return redirect('CTF_App:article_detail', pk=article.id)
    else:
        form = SectionForm()
    return render(request, 'CTF_App/add_section.html', {'form': form, 'article': article})


@login_required
def edit_section(request, section_id):
    section = get_object_or_404(Sections, id=section_id)
    if request.method == 'POST':
        form = SectionForm(request.POST, request.FILES, instance=section)
        if form.is_valid():
            form.save()
            return redirect(reverse('CTF_App:article_detail', args=[str(section.article.id)]))
    else:
        form = SectionForm(instance=section)

    return render(request, 'CTF_App/edit_section.html', {'form': form})


@login_required
def delete_section(request, section_id):
    section = get_object_or_404(Sections, id=section_id)
    article_id = section.article.id
    section.delete()
    return redirect(reverse('CTF_App:article_detail', args=[str(article_id)]))


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content', 'result']
        widgets = {
            'content': forms.TextInput(attrs={'class': 'form-control'}),
            'result': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


def take_test(request, article_id):
    article = get_object_or_404(Articles, id=article_id)
    test = get_object_or_404(Test, id=article.test.id)
    questions_in_test = QuestionInTest.objects.filter(test=test)
    questions = [qit.question for qit in questions_in_test]

    if request.method == 'POST':
        score = 0
        total = len(questions)
        for question in questions:
            correct_answers = Answer_Question.objects.filter(question=question, answer__result=True)
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id and int(selected_answer_id) in [ca.answer.id for ca in correct_answers]:
                score += 1
        return render(request, 'CTF_App/test_result.html', {'score': score, 'total': total})

    return render(request, 'CTF_App/take_test.html', {'article': article, 'questions': questions})


@login_required
def edit_test(request, article_id):
    article = get_object_or_404(Articles, id=article_id)
    test, created = Test.objects.get_or_create(id=article.test.id if article.test else None)

    QuestionInTestFormSet = inlineformset_factory(Test, QuestionInTest, fields=('question',), extra=1, can_delete=True)

    if request.method == 'POST':
        formset = QuestionInTestFormSet(request.POST, instance=test)
        if formset.is_valid():
            formset.save()
            return redirect('CTF_App:article_detail', article_id=article_id)
    else:
        formset = QuestionInTestFormSet(instance=test)

    return render(request, 'CTF_App/edit_test.html', {
        'article': article,
        'formset': formset,
    })
