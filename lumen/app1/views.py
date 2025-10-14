from django.shortcuts import render
from .models import Artigos, Bullets, Progresso, Progresso_diario

# Create your views here.

def sugerir_leitura(request, artigo_id):
    artigo_atual_id =artigo_id
    artigo_atual=Artigos.objects.get(id=artigo_atual_id)
    categoria=artigo_atual.categoria
    sugestoes=Artigos.objects.order_by('-data_publicacao').filter(categoria=categoria).exclude(id=artigo_atual_id)[:5]
    context={'artigo_atual':artigo_atual,'sugestoes':sugestoes}
    return render(request,'sugestao.html',context)

def home_page(request):
    manchete_principal = Artigos.objects.order_by('-data_publicacao').first()
    mais_recentes = []
    if manchete_principal:
        mais_recentes = Artigos.objects.order_by('-data_publicacao').exclude(id=manchete_principal.id)[:6]
    else:
        mais_recentes = Artigos.objects.order_by('-data_publicacao')[:6]
    artigos_opiniao = Artigos.objects.filter(categoria='Opinião').order_by('-data_publicacao')[:4]
    artigos_politica = Artigos.objects.filter(categoria='Política').order_by('-data_publicacao')[:4]
    
    context = {
        'manchete_principal': manchete_principal,
        'mais_recentes': mais_recentes,
        'artigos_opiniao': artigos_opiniao,
        'artigos_politica': artigos_politica, 
    }
    return render(request, 'app1/home.html', context)

def bullets(request,artigo_id):
    bullets=Artigos.objects.get(id=artigo_id).bullets.all()
    context={'bullets':bullets}
    return render(request,'bullets.html',context)