from CTF_App.views_api import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'comments', CommentViewSet)
router.register(r'tests', TestViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'questions-in-test', QuestionInTestViewSet)
router.register(r'answers', AnswerViewSet)
router.register(r'custom-users', CustomUserViewSet)

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path("debug/", include("debug_toolbar.urls")),
                  path("", include("CTF_App.urls")),
                  path("api/", include(router.urls)),
                  path('api/auth/register/', RegisterView.as_view(), name='register'),
                  path('api/auth/login/', LoginView.as_view(), name='login'),
                  path('api/create-module/', CreatemoduleView.as_view(), name='create-module'),
                  path('api/auth/update-email/', EmailUpdateView.as_view(), name='update-email'),
                  path('api/auth/change-password/', PasswordChangeView.as_view(), name='change-password'),
                  path('api/tests/<int:test_id>/', TestDetailView.as_view(), name='test-detail'),
                  path('api/auth/logout/', LogoutView.as_view(), name='logout'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
