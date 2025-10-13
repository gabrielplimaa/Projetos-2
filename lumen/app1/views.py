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


