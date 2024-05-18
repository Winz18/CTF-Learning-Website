from django.urls import path
from . import views

app_name = 'CTF_App'

urlpatterns = [
    # URL pattern cho trang chủ
    path('', views.IndexView.as_view(), name='index'),

    # URL pattern cho trang chi tiết bài viết
    path('<uuid:pk>/', views.DetailView.as_view(), name='article_detail'),
]
