from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Exam, Question, Answer, Choice
from .forms import ExamForm, QuestionForm, ChoiceForm
from django.http import JsonResponse

User = get_user_model()  # 🔸 Usar CustomUser

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
        exam = context['exam']

        # Obtener respuestas para cada pregunta
        questions_with_answers = []
        for question in exam.questions.all():
            answers = Answer.objects.filter(question=question)
            questions_with_answers.append({'question': question, 'answers': answers})

        context['questions_with_answers'] = questions_with_answers
        return context


# 🔹 AGREGAR EXAMEN (Solo profesores)
@login_required
def add_exam(request):
    if not request.user.is_teacher:
        return render(request, 'exams/unauthorized.html')

    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.teacher = request.user
            exam.save()
            messages.success(request, "Examen creado exitosamente.")
            return redirect('add_question', exam_id=exam.id)
    else:
        form = ExamForm()

    return render(request, 'exams/add_exam.html', {'form': form})


# 🔹 AGREGAR PREGUNTAS DINÁMICAS A UN EXAMEN
@login_required
def add_question(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.user != exam.teacher:
        return render(request, 'exams/unauthorized.html')

    if request.method == 'POST':
        i = 0
        while True:
            question_text = request.POST.get(f'question_text_{i}')
            question_type = request.POST.get(f'question_type_{i}')

            if question_text and question_type:
                question = Question.objects.create(
                    exam=exam,
                    text=question_text,
                    question_type=question_type
                )

                if question_type == 'multiple_choice':
                    for j in range(4):
                        choice_text = request.POST.get(f'choices_{i}_{j}')
                        if choice_text:
                            is_correct = int(request.POST.get(f'correct_choice_{i}', -1)) == j
                            Choice.objects.create(
                                question=question,
                                text=choice_text,
                                is_correct=is_correct
                            )
            else:
                break
            i += 1

        return redirect('exam_detail', pk=exam.id)

    return render(request, 'exams/add_question.html', {'exam': exam})


# 🔹 AGREGAR OPCIONES A UNA PREGUNTA (Vista alternativa)
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


# 🔹 ENVIAR RESPUESTAS DE UN EXAMEN
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

        return redirect("exam_list")

    return render(request, "exams/exam_detail.html", {"exam": exam})


# 🔹 RESULTADOS DEL EXAMEN
@login_required
def exam_results(request, pk):
    exam = get_object_or_404(Exam, pk=pk)

    if request.user != exam.teacher:
        return render(request, 'exams/unauthorized.html')

    students = User.objects.filter(answers__question__exam=exam).distinct()
    student_id = request.GET.get("student_id")
    selected_student = None
    results = {}

    if student_id:
        selected_student = get_object_or_404(User, pk=student_id)
        questions = exam.questions.all()
        for question in questions:
            answers = question.answers.filter(student=selected_student)
            results[question] = answers

    score = 0
    total = exam.questions.count()
    if selected_student and results:
        for question, answers in results.items():
            for answer in answers:
                if question.question_type == "multiple_choice":
                    if answer.selected_choice and answer.selected_choice.is_correct:
                        score += 1
                elif question.question_type == "open":
                    if answer.is_correct:
                        score += 1

    return render(request, 'exams/exam_results.html', {
        'exam': exam,
        'students': students,
        'results': results,
        'selected_student': selected_student,
        'score': score,
        'total': total
    })


# 🔹 AGREGAR PREGUNTAS MASIVAMENTE (no necesario si usas la dinámica)
@login_required
def add_question_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == "POST":
        question_texts = request.POST.getlist("question_text")
        question_types = request.POST.getlist("question_type")

        for i, question_text in enumerate(question_texts):
            question_type = question_types[i]

            question = Question.objects.create(
                exam=exam,
                text=question_text,
                question_type=question_type
            )

            if question_type == "multiple_choice":
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


# 🔹 CALIFICAR RESPUESTA ABIERTA MANUALMENTE
@login_required
def grade_open_answer(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)

    if request.user != answer.question.exam.teacher:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    if request.method == "POST":
        is_correct = request.POST.get("is_correct") == "true"
        answer.is_correct = is_correct
        answer.save()
        return JsonResponse({'success': True, 'is_correct': answer.is_correct})

    return JsonResponse({'error': 'Método no permitido'}, status=405)


# 🔹 EDITAR PREGUNTA
@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.user != question.exam.teacher:
        return render(request, 'exams/unauthorized.html')

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()

            if question.question_type == 'multiple_choice':
                question.choices.all().delete()

                choices = request.POST.getlist('choice_text')
                correct_index = int(request.POST.get('correct_choice', -1))
                for i, text in enumerate(choices):
                    Choice.objects.create(
                        question=question,
                        text=text,
                        is_correct=(i == correct_index)
                    )

            messages.success(request, "Pregunta actualizada exitosamente.")
            return redirect('exam_detail', pk=question.exam.id)
    else:
        form = QuestionForm(instance=question)
        choices = question.choices.all() if question.question_type == 'multiple_choice' else None

    return render(request, 'exams/edit_question.html', {
        'form': form,
        'question': question,
        'choices': choices,
    })


# 🔹 ELIMINAR PREGUNTA
@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if request.user != question.exam.teacher:
        return render(request, 'exams/unauthorized.html')

    if request.method == 'POST':
        exam_id = question.exam.id
        question.delete()
        messages.success(request, "Pregunta eliminada correctamente.")
        return redirect('exam_detail', pk=exam_id)

    return render(request, 'exams/confirm_delete.html', {'question': question})
