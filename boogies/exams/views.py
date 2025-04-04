from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Exam, Question, Answer, Choice
from .forms import ExamForm, QuestionForm, ChoiceForm, AnswerForm  # Asegúrate de tener estos formularios


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = context['exam']  # Obtenemos el examen

        # Obtener las respuestas de cada pregunta
        questions_with_answers = []
        for question in exam.questions.all():
            answers = Answer.objects.filter(question=question)  # Filtrar respuestas por pregunta
            questions_with_answers.append({'question': question, 'answers': answers})

        context['questions_with_answers'] = questions_with_answers  # Añadir las preguntas con respuestas al contexto
        return context


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
    exam = get_object_or_404(Exam, pk=pk)
    student = request.user

    if request.method == "POST":
        for question in exam.questions.all():
            answer_key = f"answer_{question.id}"
            if answer_key in request.POST:
                if question.question_type == "open":
                    answer_text = request.POST[answer_key]
                    Answer.objects.create(
                        question=question,
                        student=student,
                        text=answer_text
                    )
                elif question.question_type == "multiple_choice":
                    choice_id = request.POST[answer_key]
                    choice = get_object_or_404(Choice, id=choice_id)
                    Answer.objects.create(
                        question=question,
                        student=student,
                        selected_choice=choice
                    )

        # Redirigir de nuevo a la vista de detalles del examen después de enviar las respuestas
        return redirect('exam_detail', pk=exam.pk)

    return render(request, "exams/exam_detail.html", {"exam": exam})


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
        # Obtener todas las preguntas enviadas
        question_texts = request.POST.getlist("question_text")
        question_types = request.POST.getlist("question_type")

        for i, question_text in enumerate(question_texts):
            question_type = question_types[i]

            # Crear la pregunta
            question = Question.objects.create(
                exam=exam,
                text=question_text,
                question_type=question_type
            )

            # Procesar opciones si es de tipo múltiple
            if question_type == "multiple_choice":
                # Cada grupo de opciones tiene un name como choices_0, choices_1, etc.
                choices_key = f"choices_{i}"
                correct_key = f"correct_choice_{i}"
                
                choices = request.POST.getlist(choices_key)
                correct_choice_index = int(request.POST.get(correct_key, -1))

                for index, choice_text in enumerate(choices):
                    Choice.objects.create(
                        question=question,
                        text=choice_text,
                        is_correct=(index == correct_choice_index)
                    )

        return redirect("exam_detail", pk=exam.id)

    return render(request, "exams/add_question.html", {"exam": exam})


@login_required
def submit_answer(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    student = request.user

    if request.method == "POST":
        for question in exam.questions.all():
            answer_key = f"answer_{question.id}"
            if answer_key in request.POST:
                if question.question_type == "open":
                    answer_text = request.POST[answer_key]
                    Answer.objects.create(
                        question=question,
                        student=student,
                        text=answer_text
                    )
                elif question.question_type == "multiple_choice":
                    choice_id = request.POST[answer_key]
                    choice = get_object_or_404(Choice, id=choice_id)
                    Answer.objects.create(
                        question=question,
                        student=student,
                        selected_choice=choice
                    )

        return redirect("exam_results", pk=exam.id)  # Redirigir a la página de resultados

    return render(request, "exam_detail.html", {"exam": exam})

