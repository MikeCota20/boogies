from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Exam, Question, Answer, Choice
from django.contrib.auth.decorators import login_required

class ExamListView(ListView):
    model = Exam
    template_name = 'exams/exam_list.html'
    context_object_name = 'exams'

class ExamDetailView(DetailView):
    model = Exam
    template_name = 'exams/exam_detail.html'
    context_object_name = 'exam'

@login_required
def submit_answer(request, pk):
    question = get_object_or_404(Question, pk=pk)

    if request.method == 'POST':
        if question.question_type == 'open':
            text = request.POST.get('answer_text')
            Answer.objects.create(question=question, student=request.user, text=text)
        elif question.question_type == 'multiple_choice':
            choice_id = request.POST.get('answer_choice')
            choice = get_object_or_404(Choice, id=choice_id)
            Answer.objects.create(question=question, student=request.user, selected_choice=choice)

        return redirect('exam_detail', pk=question.exam.pk)

    return render(request, 'exams/submit_answer.html', {'question': question})


def exam_results(request, pk):
    exam = get_object_or_404(Exam, pk=pk)

    # Solo el profesor que creó el examen puede ver los resultados
    if request.user != exam.teacher:
        return render(request, 'exams/unauthorized.html')

    # Obtener todas las respuestas agrupadas por pregunta
    questions = exam.questions.all()
    results = {question: question.answers.all() for question in questions}

    return render(request, 'exams/exam_results.html', {'exam': exam, 'results': results})