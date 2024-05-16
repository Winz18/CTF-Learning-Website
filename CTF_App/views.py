from django.db.models import F
from django.views import generic

from .models import Article


class IndexView(generic.ListView):
    template_name = "CTF_App/index.html"
    context_object_name = "latest_article_list"
    model = Article

    def get_queryset(self):
        return Article.objects.order_by(F("date").desc())

class DetailView(generic.DetailView):
    template_name = "CTF_App/article_detail.html"
    model = Article