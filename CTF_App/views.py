from django.db.models import F
from django.views import generic
from django.shortcuts import get_object_or_404
from .models import Articles


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
