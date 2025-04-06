from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Exam(models.Model):
    title = models.CharField(max_length=255)
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'is_teacher': True}, related_name="exams"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = [
        ('open', 'Pregunta Abierta'),
        ('multiple_choice', 'Opción Múltiple')
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='open')

    def __str__(self):
        return self.text[:50]

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)  # Indica si es la respuesta correcta

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'is_student': True}, related_name="answers"
    )
    text = models.TextField(blank=True, null=True)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, blank=True, null=True)
    is_correct = models.BooleanField(null=True, blank=True)  # ✅ Para preguntas abiertas
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.question.text[:30]}"
