from django.urls import path
from . import views # Importa o arquivo views.py do app

urlpatterns = [
    # Caminho 1: A página inicial ('') chama a view 'home_page'.
    path('', views.home_page, name='home'),
    # Caminho 2: A página de sugestão chama a view 'sugerir_leitura'.
    path('sugestao/<int:artigo_id>/', views.sugerir_leitura, name='sugestao'),
    path('bullets/<int:artigo_id>/', views.bullets, name='bullets'),
]