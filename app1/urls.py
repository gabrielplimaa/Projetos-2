from django.urls import path
from . import views # Importa o arquivo views.py do app

urlpatterns = [
    # Caminho 1: A página inicial ('') chama a view 'home_page'.
    path('', views.home_page, name='home'),
    # Caminho 2: A página de sugestão chama a view 'sugerir_leitura'.
    path('sugestao/<int:artigo_id>/', views.sugerir_leitura, name='sugestao'),
    path('bullets/<int:artigo_id>/', views.bullets, name='bullets'),
    path('artigo/<int:artigo_id>/audio/', views.artigo_audio, name='artigo_audio'),
    path('politica/', views.topico_politica, name='topico_politica'),
    path('pernambuco/', views.topico_pernambuco, name='topico_pernambuco'),
    path('esportes/', views.topico_esportes, name='topico_esportes'),
    path('cultura/', views.topico_cultura, name='topico_cultura'),
    path('artigo/<int:artigo_id>/',views.exibir_artigo, name='exibir_artigo'),
    path('artigo/<int:id_artigo>/contexto/', views.conteudo_de_contexto, name='conteudo_de_contexto'),
]