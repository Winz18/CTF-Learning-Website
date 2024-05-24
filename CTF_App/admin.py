from django.contrib import admin
from .models import Test, Articles, AuthorOfArticle, Question, QuestionInTest, Answer, CustomUser


admin.site.register(Test)
admin.site.register(Articles)
admin.site.register(AuthorOfArticle)
admin.site.register(Question)
admin.site.register(QuestionInTest)
admin.site.register(Answer)
admin.site.register(CustomUser)
