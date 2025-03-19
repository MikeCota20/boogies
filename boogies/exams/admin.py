from django.contrib import admin
from .models import Exam, Question, Choice, Answer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3  # Mínimo 3 opciones por pregunta

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

admin.site.register(Exam)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Answer)
