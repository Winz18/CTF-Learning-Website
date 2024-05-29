from django.contrib import admin
from .models import *

admin.site.register(Test)
admin.site.register(Articles)
admin.site.register(AuthorOfArticle)
admin.site.register(Question)
admin.site.register(QuestionInTest)
admin.site.register(Answer)
admin.site.register(CustomUser)
admin.site.register(Comment)
