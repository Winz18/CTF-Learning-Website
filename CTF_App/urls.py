from django.urls import path
from . import views

app_name = 'CTF_App'

urlpatterns = [
    # URL pattern cho trang chủ
    path('', views.IndexView.as_view(), name='index'),

    # URL pattern cho trang chi tiết bài viết
    path('articles/<uuid:pk>/', views.DetailView.as_view(), name='article_detail'),

    # URL pattern cho trang xếp hạng
    path('scoreboard/', views.ScoreboardView.as_view(), name='scoreboard'),

    # URL pattern cho trang đăng nhập
    path('login/', views.user_login, name='login'),

    # URL pattern cho trang đăng xuất
    path('logout/', views.user_logout, name='logout'),

    # URL pattern cho trang đăng ký
    path('signup/', views.user_signup, name='signup'),
]
