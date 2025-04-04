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

class AnswerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        exam = kwargs.pop('exam')  # Recibe el examen como argumento
        super().__init__(*args, **kwargs)
        
        for question in exam.questions.all():
            if question.question_type == 'open':
                self.fields[f'answer_{question.id}'] = forms.CharField(widget=forms.Textarea, required=True)
            elif question.question_type == 'multiple_choice':
                choices = [(choice.id, choice.text) for choice in question.choices.all()]
                self.fields[f'answer_{question.id}'] = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, required=True)
