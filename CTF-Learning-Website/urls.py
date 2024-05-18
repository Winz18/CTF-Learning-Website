from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("debug/", include("debug_toolbar.urls")),
    path("", include("CTF_App.urls")),
]
