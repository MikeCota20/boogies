from django import forms
from .models import Exam, Question, Choice

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        exclude = ['teacher']  # Excluye el campo teacher

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type']  # No necesitas que el campo exam sea manejado en el formulario


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['question', 'text', 'is_correct']
