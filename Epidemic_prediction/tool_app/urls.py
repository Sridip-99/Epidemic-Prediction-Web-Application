from django.urls import path
from . import views

urlpatterns = [
    path('tool/', views.tool_view, name='Tool'),
    path('result/', views.upload_and_predict, name='upload_and_predict'),
    path('result_view/', views.result_view, name='result_view'),
    path('result_view/no_dataset', views.no_dataset_view, name='no_dataset'),
]