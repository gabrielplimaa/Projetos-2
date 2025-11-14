from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Artigos, Progresso_diario, Progresso
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from gtts import gTTS #tem que baixar essa biblioteca do google
import io #manipulação de arquivos em memoria ram
# Create your views here.
from django.utils import timezone
from app1.utils.ai import gerar_contexto
from django.contrib.auth import logout

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
    flag= False
    artigo=get_object_or_404(Artigos, id=artigo_id)
    hoje=timezone.now().date()
    visitante = request.META.get('REMOTE_ADDR', 'anonimo')
    diario,created=Progresso_diario.objects.get_or_create(data=hoje, visitante=visitante)
    if 'artigos_lidos' not in request.session:
        request.session['artigos_lidos'] = []
    if artigo_id not in request.session['artigos_lidos']:
        diario.artigos_lidos += 1
        diario.save()
        request.session['artigos_lidos'].append(artigo_id)
        request.session.modified = True
    mensagem=""
    artigo_lidos_na_sessao=len(request.session['artigos_lidos'])
    if artigo_lidos_na_sessao>1:
        mensagem=f"Você leu {artigo_lidos_na_sessao} artigos nesta sessão."
    usuario_autenticado=request.user.is_authenticated
    if usuario_autenticado:
        progresso,created=Progresso.objects.get_or_create(user=request.user, artigo=artigo)
        if not progresso.completado:
            progresso.completado=True
            progresso.save()
        quantidade_artigos_lidos=Progresso.objects.filter(user=request.user, completado=True,date=hoje).count()
        if quantidade_artigos_lidos==3:
            flag=True
        else:
            flag=False
    context={'artigo':artigo, 'mensagem':mensagem, 'flag':flag}
    return render(request, 'app1/exibir_artigo.html', context)

def conteudo_de_contexto(request,id_artigo):
    artigo=Artigos.objects.get(id=id_artigo)
    contexto_gerado=gerar_contexto(artigo.conteudo)
    context={'artigo':artigo,'contexto_gerado':contexto_gerado}
    return render(request,'app1/conteudo_de_contexto.html',context)

def cadastro(request):
    errors = []
    username = ""
    password1 = ""
    password2 = ""
    email = ""

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "").strip()
        password2 = request.POST.get("password2", "").strip()

        if not username:
            errors.append("O nome de usuário é obrigatório.")
        if not password1 or not password2:
            errors.append("A senha e a confirmação são obrigatórias.")
        elif password1 != password2:
            errors.append("As senhas não coincidem.")
        elif User.objects.filter(username=username).exists():
            errors.append("Esse nome de usuário já está em uso.")

        if not errors:
            user = User.objects.create_user(username=username, password=password1)
            authenticated_user = authenticate(username=username, password=password1)

            if authenticated_user:
                login(request, authenticated_user)
                return redirect("home")

    context = {"errors": errors, "username": username}
    return render(request, "app1/cadastro.html", context)

def login_view(request):
    return render(request, 'app1/login.html', {})

def login_existente(request):
    errors = None

    if request.method != 'POST':
        usuario = ""
        email= ""
        senha = ""
    else:
        usuario = request.POST.get("login")
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        if usuario and senha:
            user = authenticate(username=usuario, password=senha, email=email)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))
            else:
                errors = "Usuário ou senha inválidos."
        else:
            errors = "Preencha todos os campos."

    context = {
        'usuario': usuario,
        'senha': senha,
        'errors': errors,
    }
    return render(request, 'app1/login_existente.html', context)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))