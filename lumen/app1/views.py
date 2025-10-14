from django.shortcuts import render
from .models import Artigos, Sugestao, Progresso, Progresso_diario

# Create your views here.

def sugerir_leitura(request, artigo_id):
    artigo_atual_id =artigo_id
    artigo_atual=Artigos.objects.get(id=artigo_atual_id)
    categoria=artigo_atual.categoria
    sugestoes=Artigos.objects.order_by('-data_publicacao').filter(categoria=categoria).exclude(id=artigo_atual_id)[:5]
    context={'artigo_atual':artigo_atual,'sugestoes':sugestoes}
    return render(request,'sugestao.html',context)
def home_page(request):
    # 1. Busca pela Manchete Principal (o artigo mais recente)
    manchete_principal = Artigos.objects.order_by('-data_publicacao').first()
    # 2. Busca pelas notícias "Mais Recentes"
    # Se a manchete existir, a excluímos da lista para não repetir.
    mais_recentes = []
    if manchete_principal:
        mais_recentes = Artigos.objects.order_by('-data_publicacao').exclude(id=manchete_principal.id)[:6]
    else:
        # Caso o banco de dados esteja vazio, evita um erro.
        mais_recentes = Artigos.objects.order_by('-data_publicacao')[:6]
    # 3. Busca por artigos de Opinião
    # Ajuste o nome da categoria se for diferente no seu banco.
    artigos_opiniao = Artigos.objects.filter(categoria='Opinião').order_by('-data_publicacao')[:4]
    # 4. Busca por uma categoria fixa para a sidebar (substituindo "De seu interesse")
    artigos_politica = Artigos.objects.filter(categoria='Política').order_by('-data_publicacao')[:4]
    # Monta o 'context' com todas as nossas listas de artigos.
    context = {
        'manchete_principal': manchete_principal,
        'mais_recentes': mais_recentes,
        'artigos_opiniao': artigos_opiniao,
        'artigos_politica': artigos_politica, # Nova seção!
    }
    return render(request, 'app1/home.html', context)