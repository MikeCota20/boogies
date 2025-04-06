from django.urls import path
from .views import (
    ExamListView,
    ExamDetailView,
    submit_answer,
    exam_results,
    add_question,
    add_exam,
    add_question_view,
    grade_open_answer,
    edit_question,
    delete_question
)

urlpatterns = [
    path("", ExamListView.as_view(), name="exam_list"),
    path("<int:pk>/", ExamDetailView.as_view(), name="exam_detail"),
    path("<int:pk>/submit/", submit_answer, name="submit_answer"),
    path("<int:pk>/results/", exam_results, name="exam_results"),

    path("add/", add_exam, name="create_exam"),
    path("exam/<int:exam_id>/add-question/", add_question, name="add_question"),
    path("<int:exam_id>/add_question/", add_question_view, name="add_question_view"),

    path("grade-answer/<int:answer_id>/", grade_open_answer, name="grade_open_answer"),
    path("question/<int:question_id>/edit/", edit_question, name="edit_question"),
    path("question/<int:question_id>/delete/", delete_question, name="delete_question"),
]
