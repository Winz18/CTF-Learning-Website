from django.urls import path

from . import views

app_name = "CTF_App"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="article_detail"),
]
