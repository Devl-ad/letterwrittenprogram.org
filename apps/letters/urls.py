from django.urls import path
from . import views

app_name = 'letters'

urlpatterns = [
    path('write/', views.write_letter, name='write'),
    path('', views.letter_list, name='list'),
    path('<int:pk>/', views.letter_detail, name='detail'),
]
