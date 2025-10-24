from django.http import FileResponse
from django.shortcuts import render
from .models import Artigos, Bullets, Progresso, Progresso_diario
from django.shortcuts import get_object_or_404
from gtts import gTTS #tem que baixar essa biblioteca do google
import io #manipulação de arquivos em memoria ram
# Create your views here.
from django.utils import timezone

def sugerir_leitura(request, artigo_id):
    artigo_atual_id =artigo_id
    artigo_atual=Artigos.objects.get(id=artigo_atual_id)
    categoria=artigo_atual.categoria
    sugestoes=Artigos.objects.order_by('-data_publicacao').filter(categoria=categoria).exclude(id=artigo_atual_id)[:5]
    context={'artigo_atual':artigo_atual,'sugestoes':sugestoes}
    return render(request,'app1/sugestao.html',context)

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
    return render(request,'app1/bullets.html',context)

def artigo_audio(request, artigo_id): 
    artigo = get_object_or_404(Artigos,id=artigo_id)
    texto = artigo.conteudo
    tts = gTTS(text=texto, lang='pt',slow=False)
    buffer = io.BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return FileResponse(buffer,content_type='audio/mpeg')
    
    # n salva o audio no banco de dados, gera na hora e manda pro usuario, salvando no buffer, que é um arquivo em memoria ram(memoria volátil)
    #quando o usuario fecha a pagina, o audio some, n fica salvo no servidor


def topico_politica(request):
    artigos_politica = Artigos.objects.filter(categoria='Política').order_by('-data_publicacao')
    context = {'artigos_politica': artigos_politica}
    return render(request, 'app1/topico_politica.html', context)

def topico_pernambuco(request):
    artigos_pernambuco = Artigos.objects.filter(categoria='Pernambuco').order_by('-data_publicacao')
    context = {'artigos_pernambuco': artigos_pernambuco}
    return render(request, 'app1/topico_pernambuco.html', context)

def topico_esportes(request):
    artigos_esportes = Artigos.objects.filter(categoria='Esportes').order_by('-data_publicacao')
    context = {'artigos_esportes': artigos_esportes}
    return render(request, 'app1/topico_esportes.html', context)

def topico_cultura(request):
    artigos_cultura = Artigos.objects.filter(categoria='Cultura').order_by('-data_publicacao')
    context = {'artigos_cultura': artigos_cultura}
    return render(request, 'app1/topico_cultura.html', context)


def exibir_artigo(request, artigo_id):
    artigo=get_object_or_404(Artigos, id=artigo_id)
    context={'artigo':artigo}
    return render(request, 'app1/exibir_artigo.html', context)