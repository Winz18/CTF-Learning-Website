from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import F
from django.forms import inlineformset_factory, modelformset_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.core import serializers
from .models import Articles, Sections, Test, QuestionInTest, Question, Answer, CustomUser, Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class IndexView(generic.ListView):
    template_name = "CTF_App/index.html"
    context_object_name = "latest_article_list"
    model = Articles
    paginate_by = 5

    def get_queryset(self):
        category = self.request.GET.get('category')
        search_query = self.request.GET.get('search')

        queryset = Articles.objects.all()

        if category:
            queryset = queryset.filter(category=category)

        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset.order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')

        # Pagination
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)

        context['latest_article_list'] = articles
        context['search_query'] = search_query
        context['page_obj'] = articles  # Added for built-in pagination support

        return context


class DetailView(generic.DetailView):
    template_name = "CTF_App/article_detail.html"
    model = Articles
    context_object_name = "article"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = self.object.sections.order_by('position')
        context['avatar'] = self.object.author.customuser.avatar.url
        context['comments'] = Comment.objects.filter(article=self.object)
        context['comment_form'] = CommentForm()
        return context

    def get_object(self, queryset=None):
        if not hasattr(self, '_article'):
            self._article = super().get_object(queryset)
            self._article.total_views += 1
            self._article.save()
        return self._article

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.article = self.get_object()
            comment.save()
        return redirect('CTF_App:article_detail', pk=self.get_object().pk)


class ScoreboardView(generic.ListView):
    template_name = 'CTF_App/scoreboard.html'
    context_object_name = 'users'
    model = User

    def get_queryset(self):
        return User.objects.annotate(
            score=F('customuser__score'),
            contribution=F('customuser__contribution')
        ).order_by('-score', '-contribution')


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
            rank=0,
            avatar='default.jpg'
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
        'avatar': CustomUser.objects.get(user=current_user).avatar.url,
        'score': CustomUser.objects.get(user=current_user).score,
        'contribution': CustomUser.objects.get(user=current_user).contribution,
        'rank': rank,
    }
    return render(request, 'CTF_App/profile.html', context)


@login_required
def change_avatar(request):
    if request.method == 'POST':
        avatar = request.FILES['avatar']
        custom_user = CustomUser.objects.get(user=request.user)
        custom_user.avatar.delete()
        custom_user.avatar = avatar
        custom_user.save()
        return redirect('CTF_App:profile')
    return render(request, 'CTF_App/change_avatar.html')


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
        valid_categories = ['Web Security', 'Cryptography', 'Reverse Engineering', 'Forensics', 'Binary Exploitation',
                            'Misc']
        if form.instance.category not in valid_categories:
            form.add_error('category', 'Invalid category')
            return self.form_invalid(form)

        # Save the form first
        response = super().form_valid(form)

        # Increment the 'contribution' field of the author's CustomUser instance
        self.request.user.customuser.contribution += 1
        self.request.user.customuser.save()

        return response

    def get_success_url(self):
        return reverse('CTF_App:article_detail', kwargs={'pk': self.object.pk})


@login_required
def add_section(request, article_id, position=None):
    article = get_object_or_404(Articles, id=article_id)
    if request.user != article.author:
        return redirect('CTF_App:article_detail', pk=article.id)

    if request.method == 'POST':
        form = SectionForm(request.POST, request.FILES)
        if form.is_valid():
            new_section = form.save(commit=False)
            new_section.article = article

            if position is not None:
                # Update positions of other sections to make room for the new section
                Sections.objects.filter(article=article, position__gte=position).update(position=F('position') + 1)
                new_section.position = position
            else:
                # If no position specified, add to the end
                new_section.position = article.sections.count() + 1

            new_section.save()
            return redirect('CTF_App:article_detail', pk=article.id)
    else:
        form = SectionForm()

    return render(request, 'CTF_App/add_section.html', {'form': form, 'article': article, 'position': position})


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


@login_required
def delete_article(request, article_id):
    article = get_object_or_404(Articles, id=article_id)
    article.sections.all().delete()
    article.delete()
    article.author.customuser.contribution -= 1
    article.author.customuser.save()
    return redirect(reverse('CTF_App:index'))


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

    # If the user has already taken the test, redirect them to the result page
    if request.user.customuser.score != 0:
        return render(request, 'CTF_App/test_result.html', {'score': request.user.customuser.score, 'total': len(questions)})

    # If the article has no test, redirect them to the article detail page
    if not questions:
        return redirect('CTF_App:article_detail', pk=article_id)

    if request.method == 'POST':
        score = 0
        total = len(questions)
        for question_data in questions_in_test:
            question = question_data.question
            correct_answers = Answer.objects.filter(question=question, result=True)
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id and int(selected_answer_id) in [ca.id for ca in correct_answers]:
                score += 1
            request.user.customuser.score = score
            request.user.customuser.save()
        return render(request, 'CTF_App/test_result.html', {'score': score, 'total': total})

    return render(request, 'CTF_App/take_test.html', {'article': article, 'questions_in_test': questions_in_test})


@login_required
def edit_test(request, article_id):
    article = get_object_or_404(Articles, id=article_id)
    test, created = Test.objects.get_or_create(id=article.test.id if article.test else None)
    QuestionInTestFormSet = inlineformset_factory(Test, QuestionInTest, fields=('question',), extra=1,
                                                  can_delete=True)
    AnswerFormSet = inlineformset_factory(Question, Answer, fields=('content', 'result'), extra=1, can_delete=True)

    if request.method == 'POST':
        formset = QuestionInTestFormSet(request.POST, instance=test)
        if formset.is_valid():
            formset.save()

            for form in formset:
                if form.instance.pk and form.instance.question:
                    question = form.instance.question
                    answer_formset = AnswerFormSet(request.POST, instance=question, prefix=f'answer_{question.id}')
                    if answer_formset.is_valid():
                        answer_formset.save()

            messages.success(request, 'Test edited successfully')
            return redirect('CTF_App:edit_test', article_id=article_id)
    else:
        formset = QuestionInTestFormSet(instance=test)
        formset_with_answers = []
        for form in formset:
            if form.instance.pk and form.instance.question:
                question = form.instance.question
                answer_formset = AnswerFormSet(instance=question, prefix=f'answer_{question.id}')
                formset_with_answers.append((form, answer_formset))
            else:
                formset_with_answers.append((form, None))

    return render(request, 'CTF_App/edit_test.html', {
        'article': article,
        'formset': formset,
        'formset_with_answers': formset_with_answers,
    })


@login_required
def add_test(request, article_id):
    article = get_object_or_404(Articles, id=article_id)

    if request.method == 'POST':
        test = Test.objects.create(difficulty=request.POST.get('difficulty', ''))
        article.test = test
        article.save()

        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.save()

            answer_formset = modelformset_factory(Answer, form=AnswerForm, extra=2)
            formset = answer_formset(request.POST, queryset=Answer.objects.none())

            if formset.is_valid():
                for form in formset:
                    answer = form.save(commit=False)
                    answer.question = question
                    answer.save()

        return redirect('CTF_App:article_detail', pk=article_id)

    question_form = QuestionForm()
    answer_formset = modelformset_factory(Answer, form=AnswerForm, extra=2)
    formset = answer_formset(queryset=Answer.objects.none())

    return render(request, 'CTF_App/add_test.html', {
        'article': article,
        'question_form': question_form,
        'formset': formset,
    })
