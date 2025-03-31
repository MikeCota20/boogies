from django.urls import path
from .views import ExamListView, ExamDetailView, submit_answer, exam_results, add_question, add_exam, add_question_view

# urlpatterns = [
#     path('', ExamListView.as_view(), name='exam_list'),
#     path('<int:pk>/', ExamDetailView.as_view(), name='exam_detail'),
#     path('<int:pk>/results/', exam_results, name='exam_results'),
#     path('submit/<int:pk>/', submit_answer, name='submit_answer'),
# ]

# from django.urls import path
# from . import views

# urlpatterns = [
#     path("", views.exam_list, name="exam_list"),  # Lista de exámenes en /exams/
#     path("<int:exam_id>/", views.exam_detail, name="exam_detail"),  # Detalle de examen en /exams/ID/
# ]

urlpatterns = [
    path("", ExamListView.as_view(), name="exam_list"),  # Lista de exámenes en /exams/
    path("<int:pk>/", ExamDetailView.as_view(), name="exam_detail"),  # Detalles de un examen específico
    path("<int:pk>/submit/", submit_answer, name="submit_answer"),  # Enviar respuestas
    path("<int:pk>/results/", exam_results, name="exam_results"),  # Resultados del examen
    path('exam/<int:exam_id>/add-question/', add_question, name='add_question'),
    path('add/', add_exam, name='create_exam'),
    path('<int:exam_id>/add_question/', add_question_view, name='add_question'),
]