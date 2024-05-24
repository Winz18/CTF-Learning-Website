from django.urls import path, include
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

    # URL pattern cho trang profile
    path('profile/', views.profile_view, name='profile'),

    # URL pattern cho trang change_username
    path('change_username/', views.change_username, name='change_username'),

    # URL pattern cho trang change_email
    path('change_email/', views.change_email, name='change_email'),

    # URL pattern cho trang change_password
    path('change_password/', views.change_password, name='change_password'),

    # URL pattern cho trang tạo bài viết
    path('articles/new/', views.ArticleCreateView.as_view(), name='article_create'),

    # URL pattern cho trang thêm section
    path('articles/<uuid:article_id>/add_section/', views.add_section, name='add_section'),

    # URL pattern cho trang chỉnh sửa bài viết
    path('section/edit/<uuid:section_id>/', views.edit_section, name='edit_section'),
    path('section/delete/<uuid:section_id>/', views.delete_section, name='delete_section'),
    path('article/<uuid:article_id>/add_section/', views.add_section, name='add_section'),
    path('article/<uuid:article_id>/add_section/<int:position>/', views.add_section, name='add_section'),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # URL pattern cho trang làm bài test
    path('article/<uuid:article_id>/test/', views.take_test, name='take_test'),
    path('article/<uuid:article_id>/edit_test/', views.edit_test, name='edit_test'),
]
