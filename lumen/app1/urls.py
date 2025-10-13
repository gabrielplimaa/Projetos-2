from django.urls import path
from . import views

urlpatterns = [
    path('sugestao/<int:artigo_id>/', views.sugerir_leitura, name='sugestao'),
]