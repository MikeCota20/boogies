from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Exam, Question, Answer, Choice
from .forms import ExamForm, QuestionForm, ChoiceForm  # Asegúrate de tener estos formularios


# 🔹 LISTAR EXÁMENES
class ExamListView(ListView):
    model = Exam
    template_name = 'exams/exam_list.html'
    context_object_name = 'exams'


# 🔹 DETALLE DE UN EXAMEN
class ExamDetailView(DetailView):
    model = Exam
    template_name = 'exams/exam_detail.html'
    context_object_name = 'exam'


# 🔹 AGREGAR EXAMEN (Solo profesores)
@login_required
def add_exam(request):
    if not request.user.is_teacher:
        return render(request, 'exams/unauthorized.html')

    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            # Crear el examen
            exam = form.save(commit=False)
            exam.teacher = request.user  # Asignar el teacher al examen
            exam.save()

            messages.success(request, "Examen creado exitosamente.")
            return redirect('add_question_view', exam_id=exam.id)  # Redirigir a agregar preguntas

    else:
        form = ExamForm()

    return render(request, 'exams/add_exam.html', {'form': form})




# 🔹 AGREGAR PREGUNTA A UN EXAMEN (Solo profesores)
@login_required
def add_question(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.user != exam.teacher:
        return render(request, 'exams/unauthorized.html')

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            question.save()
            return redirect('exam_detail', pk=exam.id)

    else:
        form = QuestionForm()

    return render(request, 'exams/add_question.html', {'form': form, 'exam': exam})


# 🔹 AGREGAR RESPUESTAS (Opciones para preguntas de opción múltiple)
@login_required
def add_choice(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.user != question.exam.teacher:
        return render(request, 'exams/unauthorized.html')

    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            return redirect('exam_detail', pk=question.exam.id)

    else:
        form = ChoiceForm()

    return render(request, 'exams/add_choice.html', {'form': form, 'question': question})


# 🔹 ENVIAR RESPUESTA (Solo estudiantes)
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


# 🔹 VER RESULTADOS (Solo el profesor del examen)
@login_required
def exam_results(request, pk):
    exam = get_object_or_404(Exam, pk=pk)

    if request.user != exam.teacher:
        return render(request, 'exams/unauthorized.html')

    questions = exam.questions.all()
    results = {question: question.answers.all() for question in questions}

    return render(request, 'exams/exam_results.html', {'exam': exam, 'results': results})


def add_question_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == "POST":
        question_text = request.POST.get("question_text")
        question_type = request.POST.get("question_type", "open")

        # Crear la pregunta
        question = Question.objects.create(
            exam=exam,
            text=question_text,
            question_type=question_type
        )

        # Si es una pregunta de opción múltiple, agregar opciones
        if question_type == "multiple_choice":
            choices = request.POST.getlist("choices")  # Obtiene todas las opciones
            correct_choice_index = int(request.POST.get("correct_choice", -1))

            for index, choice_text in enumerate(choices):
                Choice.objects.create(
                    question=question,
                    text=choice_text,  # Aquí corregimos el nombre del campo
                    is_correct=(index == correct_choice_index)
                )

        return redirect("exam_detail", pk=exam.id)


    return render(request, "exams/add_question.html", {"exam": exam})