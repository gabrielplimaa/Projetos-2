from django.test import TestCase
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pytest, time
from unittest.mock import patch
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class bulletsPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    def abrir(self, url):
        self.driver.get(url)
    def obter_titulo(self):
        titulo = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        return titulo.text
    def obter_lista_bullets(self):
        bullets = self.driver.find_elements(By.CSS_SELECTOR, "ul li")
        return [b.text for b in bullets]
    def verificar_mensagem_vazia(self):
        return "Nenhum Ponto Chave Encontrado" in self.driver.page_source

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()

class Test_bullets:
    def test_pagina_com_bullets(self, driver):
        page = bulletsPage(driver)
        page.abrir("http://localhost:8000/pontos_chave_com_bullets/")
        titulo = page.obter_titulo()
        bullets = page.obter_lista_bullets()
        assert "Pontos Chave do Artigo" in titulo
        assert len(bullets) > 0
        assert all(b.strip() != "" for b in bullets)
    def test_pagina_sem_bullets(self, driver):
        page = bulletsPage(driver)
        page.abrir("http://localhost:8000/pontos_chave_vazio/")
        assert page.verificar_mensagem_vazia()
        assert len(page.obter_lista_bullets()) == 0

class exibir_artigo_Page:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    def abrir(self, url):
        self.driver.get(url)
    def obter_titulo(self):
        return self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text
    def verificar_audio(self):
        return self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "audio"))).is_displayed()
    def verificar_links(self):
        links = self.driver.find_elements(By.CSS_SELECTOR, ".article-actions a")
        return [l.text for l in links]
    def verificar_banner(self):
        try:
            banner = self.driver.find_element(By.ID, "banner")
            return banner.is_displayed()
        except:
            return False
    def obter_conteudo(self):
        try:
            elemento = self.driver.find_element(By.CSS_SELECTOR, ".article-content p")
            return elemento.text
        except:
            return ""

    def obter_data_publicacao(self):
        try:
            return self.driver.find_element(By.CLASS_NAME, "card-date").text
        except:
            return None

class Test_exibir_artigo:
    def test_artigo_com_banner(self, driver):
        page = exibir_artigo_Page(driver)
        page.abrir("http://localhost:8000/artigo_com_banner/")
        assert page.obter_titulo() != ""
        assert page.verificar_audio()
        links = page.verificar_links()
        assert "Sugestões de Leitura" in links
        assert "Ver Pontos Chave" in links
        assert page.verificar_banner()
        assert page.obter_conteudo().strip() != ""
        data = page.obter_data_publicacao()
        assert data is None or "Publicado em:" in data
        
    def test_artigo_sem_banner(self, driver):
        page = exibir_artigo_Page(driver)
        page.abrir("http://localhost:8000/artigo_sem_banner/")
        assert page.obter_titulo() != ""
        assert page.verificar_audio()
        links = page.verificar_links()
        assert "Sugestões de Leitura" in links
        assert "Ver Pontos Chave" in links
        assert not page.verificar_banner()
        assert page.obter_conteudo().strip() != ""
        data = page.obter_data_publicacao()
        assert data is None or "Publicado em:" in data

class Test_home:
    def test_manchete_imagem(self):
        manchete_img = self.driver.find_elements(By.CSS_SELECTOR, ".card-manchete img")
        if manchete_img:  
            src = manchete_img[0].get_attribute("src")
            assert src.strip() != ""

    def test_manchete_resumo(self):
        resumo = self.driver.find_element(By.CSS_SELECTOR, ".card-manchete .card-summary").text
        assert resumo.strip() != ""

    def test_manchete_categoria(self):
        categoria = self.driver.find_element(By.CSS_SELECTOR, ".card-manchete .card-category").text
        assert categoria.strip() != ""

    def test_mais_recentes_titulos_e_categorias(self):
        artigos = self.driver.find_elements(By.CSS_SELECTOR, ".recent-grid article")
        for artigo in artigos:
            titulo = artigo.find_element(By.CSS_SELECTOR, ".card-title a").text
            categoria = artigo.find_element(By.CSS_SELECTOR, ".card-category").text
            assert titulo.strip() != ""
            assert categoria.strip() != ""

    def setup_class(self):
        opts = Options()
        opts.add_argument("--headless")
        self.driver = webdriver.Chrome(options=opts)
        self.driver.get("http://127.0.0.1:8000/")

    def teardown_class(self):
        self.driver.quit()

    def test_titulo_pagina(self):
        assert "Jornal do Commercio" in self.driver.title

    def test_menu_links(self):
        links = self.driver.find_elements(By.CSS_SELECTOR, ".main-nav a")
        textos = [link.text for link in links]
        esperado = ["Pernambuco", "Política", "Esportes", "Cultura"]
        for e in esperado: assert e in textos

    def test_manchete_principal(self):
        manchete = self.driver.find_elements(By.CSS_SELECTOR, ".card-manchete")
        assert len(manchete) > 0
        titulo = manchete[0].find_element(By.CSS_SELECTOR, ".card-title a")
        assert titulo.text != ""

    def test_mais_recentes(self):
        recentes = self.driver.find_elements(By.CSS_SELECTOR, ".recent-grid article")
        assert len(recentes) > 0

    def test_blocos_sidebar(self):
        secoes = self.driver.find_elements(By.CSS_SELECTOR, ".sidebar .section-title")
        nomes = [s.text for s in secoes]
        assert "Política" in nomes
        assert "Opinião" in nomes

class Test_sugestão:
    @pytest.fixture(scope="class", autouse=True)
    def test_sugestoes_categoria_no_titulo(self):
        box = self.driver.find_element(By.CSS_SELECTOR, ".sugestoes-box h3").text
        assert "Sugestões de Leitura" in box
        assert "Categoria:" in box
        artigo_categoria = self.driver.find_element(By.CSS_SELECTOR, ".artigo-principal .card-date strong").text
        assert artigo_categoria.lower() in box.lower()
    
    def test_datas_sugestoes(self):
        sugestoes = self.driver.find_elements(By.CSS_SELECTOR, ".sugestoes-box ul li")
        for s in sugestoes:
            data = s.find_element(By.TAG_NAME, "small").text
            assert "/" in data #para ver o formato certo de data

    def setup_class(self):
        opts = Options()
        opts.add_argument("--headless")
        self.driver = webdriver.Chrome(options=opts)
        self.driver.get("http://127.0.0.1:8000/artigo/1/")
        yield   
        self.driver.quit()

    def test_titulo_pagina(self):
        assert "Detalhe do Artigo" in self.driver.title

    def test_header(self):
        nav = self.driver.find_elements(By.CSS_SELECTOR, ".main-nav a")
        textos = [n.text.lower() for n in nav]
        for item in ["home", "pernambuco", "política", "esportes", "cultura"]:
            assert item in textos

    def test_artigo_principal(self):
        titulo = self.driver.find_element(By.CSS_SELECTOR, ".artigo-principal h1").text
        categoria = self.driver.find_element(By.CSS_SELECTOR, ".card-date").text
        conteudo = self.driver.find_element(By.CSS_SELECTOR, ".conteudo").text
        assert titulo != ""
        assert "Categoria:" in categoria
        assert len(conteudo) > 0

    def test_sugestoes(self):
        box = self.driver.find_element(By.CSS_SELECTOR, ".sugestoes-box h3").text
        assert "Sugestões de Leitura" in box
    
        sugestoes = self.driver.find_elements(By.CSS_SELECTOR, ".sugestoes-box ul li a")
    
        if len(sugestoes) == 0:
            msg = self.driver.find_element(By.CSS_SELECTOR, ".sugestoes-box p").text
            assert "Não há mais artigos recentes nesta categoria" in msg
        else:
            assert len(sugestoes) > 0


class Test_Topico_Cultura:
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self):
        opts = Options()
        opts.add_argument("--headless")
        self.driver = webdriver.Chrome(options=opts)
        self.driver.get("http://127.0.0.1:8000/topico_cultura/")
        yield
        self.driver.quit()

    def test_titulo_pagina(self):
        assert "Tópico: Cultura" in self.driver.title

    def test_header_menu(self):
        nav = self.driver.find_elements(By.CSS_SELECTOR, ".main-nav a")
        textos = [n.text.lower() for n in nav]
        for item in ["home","política","pernambuco","esportes"]:
            assert item in textos

    def test_secao_artigos(self):
        artigos = self.driver.find_elements(By.CSS_SELECTOR, ".card .card-content")
        if artigos:
            for a in artigos:
                titulo = a.find_element(By.CSS_SELECTOR, ".card-title a").text
                categoria = a.find_element(By.CSS_SELECTOR, ".card-category").text
                data = a.find_element(By.CSS_SELECTOR, ".card-date").text if len(a.find_elements(By.CSS_SELECTOR, ".card-date"))>0 else ""
                assert titulo != "" or "Nenhum Artigo de Cultura Encontrado" in a.text
                assert categoria != "" or "Nenhum Artigo de Cultura Encontrado" in a.text
        else:
            msg = self.driver.find_element(By.TAG_NAME,"h2").text
            assert "Nenhum Artigo de Cultura Encontrado" in msg
    def test_artigos_resumo(self):
        artigos = self.driver.find_elements(By.CSS_SELECTOR, ".card .card-content")
        for a in artigos:
            if a.find_elements(By.CSS_SELECTOR, ".card-summary"):
                resumo = a.find_element(By.CSS_SELECTOR, ".card-summary").text
                assert resumo.strip() != ""
    def test_artigos_categoria_cultura(self):
        artigos = self.driver.find_elements(By.CSS_SELECTOR, ".card .card-content")
        for a in artigos:
            categoria = a.find_element(By.CSS_SELECTOR, ".card-category").text
            assert categoria.upper() == "CULTURA"
    def test_datas_artigos(self):
        artigos = self.driver.find_elements(By.CSS_SELECTOR, ".card .card-content")
        for a in artigos:
            data = a.find_element(By.CSS_SELECTOR, ".card-date").text
            assert "Publicado em:" in data
            assert "/" in data
            assert ":" in data


class Test_topico_esportes:
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self):
        opts = Options()
        opts.add_argument("--headless")
        self.driver = webdriver.Chrome(options=opts)
        self.driver.get("http://127.0.0.1:8000/topico_esportes/")
        yield
        self.driver.quit()

    def test_titulo_pagina(self):
        assert "Tópico: Esportes" in self.driver.title

    def test_header_menu(self):
        nav = self.driver.find_elements(By.CSS_SELECTOR, ".main-nav a")
        textos = [n.text.lower() for n in nav]
        for item in ["home","política","pernambuco","cultura"]:
            assert item in textos

    def test_secao_artigos(self):
        artigos = self.driver.find_elements(By.CSS_SELECTOR, ".card .card-content")
        if artigos:
            for a in artigos:
                titulo = a.find_element(By.CSS_SELECTOR, ".card-title a").text
                categoria = a.find_element(By.CSS_SELECTOR, ".card-category").text
                data = a.find_element(By.CSS_SELECTOR, ".card-date").text if len(a.find_elements(By.CSS_SELECTOR, ".card-date"))>0 else ""
                assert titulo != "" or "Nenhum Artigo de Esportes Encontrado" in a.text
                assert categoria != "" or "Nenhum Artigo de Esportes Encontrado" in a.text
        else:
            msg = self.driver.find_element(By.TAG_NAME,"h2").text
            assert "Nenhum Artigo de Esportes Encontrado" in msg
    def test_artigos_resumo(self):
        artigos = self.driver.find_elements(By.CSS_SELECTOR, ".card .card-content")
        for a in artigos:
            if a.find_elements(By.CSS_SELECTOR, ".card-summary"):
                resumo = a.find_element(By.CSS_SELECTOR, ".card-summary").text
                assert resumo.strip() != ""
    def test_artigos_categoria_esportes(self):
        artigos = self.driver.find_elements(By.CSS_SELECTOR, ".card .card-content")
        for a in artigos:
            categoria = a.find_element(By.CSS_SELECTOR, ".card-category").text
            assert categoria.upper() == "ESPORTES"
    def test_datas_artigos(self):
        artigos = self.driver.find_elements(By.CSS_SELECTOR, ".card .card-content")
        for a in artigos:
            data = a.find_element(By.CSS_SELECTOR, ".card-date").text
            assert "Publicado em:" in data
            assert "/" in data
            assert ":" in data

class Test_topico_pernambuco:
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self):
        opts = Options()
        opts.add_argument("--headless")
        self.driver = webdriver.Chrome(options=opts)
        self.driver.get("http://127.0.0.1:8000/")

    def teardown_class(self):
        self.driver.quit()

    def test_titulo_pagina(self):
        assert "Tópico: Pernambuco" in self.driver.title

    def test_header_menu(self):
        nav = self.driver.find_elements(By.CSS_SELECTOR, ".main-nav a")
        textos = [n.text.lower() for n in nav]
        for item in ["home","política","esportes","cultura"]:
            assert item in textos

    def test_secao_artigos(self):
        artigos = self.driver.find_elements(By.CSS_SELECTOR, ".card .card-content")
        if artigos:
            for a in artigos:
                titulo = a.find_element(By.CSS_SELECTOR, ".card-title a").text
                categoria = a.find_element(By.CSS_SELECTOR, ".card-category").text
                data = a.find_element(By.CSS_SELECTOR, ".card-date").text if len(a.find_elements(By.CSS_SELECTOR, ".card-date"))>0 else ""
                assert titulo != "" or "Nenhum Artigo de Pernambuco Encontrado" in a.text
                assert categoria != "" or "Nenhum Artigo de Pernambuco Encontrado" in a.text
        else:
            msg = self.driver.find_element(By.TAG_NAME,"h2").text
            assert "Nenhum Artigo de Pernambuco Encontrado" in msg
            
    def test_artigos_resumo(self):
        artigos = self.driver.find_elements(By.CSS_SELECTOR, ".card .card-content")
        for a in artigos:
            if a.find_elements(By.CSS_SELECTOR, ".card-summary"):
                resumo = a.find_element(By.CSS_SELECTOR, ".card-summary").text
                assert resumo.strip() != ""

    def test_artigos_categoria_pernambuco(self):
        artigos = self.driver.find_elements(By.CSS_SELECTOR, ".card .card-content")
        for a in artigos:
            categoria = a.find_element(By.CSS_SELECTOR, ".card-category").text
            assert categoria.upper() == "PERNAMBUCO" 

    def test_datas_artigos(self):
        artigos = self.driver.find_elements(By.CSS_SELECTOR, ".card .card-content")
        for a in artigos:
            data = a.find_element(By.CSS_SELECTOR, ".card-date").text
            assert "Publicado em:" in data
            assert "/" in data
            assert ":" in data          

class Test_topico_politica:
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self):
        opts = Options()
        opts.add_argument("--headless")
        self.driver = webdriver.Chrome(options=opts)
        self.driver.get("http://127.0.0.1:8000/topico_politica/")
        yield
        self.driver.quit()

    def test_titulo_pagina(self):
        assert "Tópico: Política" in self.driver.title

    def test_header_menu(self):
        nav = self.driver.find_elements(By.CSS_SELECTOR, ".main-nav a")
        textos = [n.text.lower() for n in nav]
        for item in ["home","pernambuco","esportes","cultura"]:
            assert item in textos

    def test_secao_artigos(self):
        artigos = self.driver.find_elements(By.CSS_SELECTOR, ".card .card-content")
        if artigos:
            for a in artigos:
                titulo = a.find_element(By.CSS_SELECTOR, ".card-title a").text
                categoria = a.find_element(By.CSS_SELECTOR, ".card-category").text
                data = a.find_element(By.CSS_SELECTOR, ".card-date").text if len(a.find_elements(By.CSS_SELECTOR, ".card-date"))>0 else ""
                assert titulo != "" or "Nenhum Artigo de Política Encontrado" in a.text
                assert categoria != "" or "Nenhum Artigo de Política Encontrado" in a.text
        else:
            msg = self.driver.find_element(By.TAG_NAME,"h2").text
            assert "Nenhum Artigo de Política Encontrado" in msg


class conteudo_contexto_Page:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def abrir(self, id_artigo):
        self.driver.get(f"http://localhost:8000/artigo/{id_artigo}/contexto/")

    def obter_titulo(self):
        return self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text

    def obter_secao(self):
        try:
            return self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2"))).text
        except:
            return None

    def obter_links(self):
        descricoes = self.driver.find_elements(By.CSS_SELECTOR, "ul li p")
        return [d.text for d in descricoes]

    def obter_mensagem_vazia(self):
        return "Nenhum contexto adicional encontrado" in self.driver.page_source

class Test_conteudo_de_contexto:
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self):
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=opts)
        yield
        self.driver.quit()

    @patch("app1.views.gerar_contexto")
    def test_exibe_links_de_contexto(self, mock_gerar_contexto):
        mock_gerar_contexto.return_value = {
            "secao": "Entenda o Contexto",
            "links": [
                {"titulo": "História do tema", "url": "https://pt.wikipedia.org/wiki/Exemplo", "descricao": "Explica o contexto histórico do artigo."},
                {"titulo": "Análise econômica", "url": "https://exemplo.com/economia", "descricao": "Aborda os impactos econômicos mencionados."}
            ]
        }
        page = conteudo_contexto_Page(self.driver)
        page.abrir(1)
        titulo = page.obter_titulo()
        assert titulo != ""
        secao = page.obter_secao()
        assert "Entenda o Contexto" in secao
        def obter_links(self):
            return self.driver.find_elements(By.CSS_SELECTOR, "ul li a")

    @patch("app1.views.gerar_contexto")
    def test_sem_links_de_contexto(self, mock_gerar_contexto):
        mock_gerar_contexto.return_value = {"secao": "", "links": []}
        page = conteudo_contexto_Page(self.driver)
        page.abrir(1)
        assert page.obter_mensagem_vazia()

class login_Page:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def abrir(self):
        self.driver.get("http://localhost:8000/login/")

    def obter_titulo_principal(self):
        return self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "login-main-title"))).text

    def obter_titulo_beneficios(self):
        return self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "login-benefits-title"))).text

    def obter_botoes(self):
        return self.driver.find_elements(By.CSS_SELECTOR, ".login-btn-primary, .login-btn-secondary")

    def obter_texto_legal(self):
        return self.driver.find_element(By.CLASS_NAME, "login-legal-text").text

    def obter_lista_beneficios(self):
        itens = self.driver.find_elements(By.CSS_SELECTOR, ".benefit-list li")
        return [i.text for i in itens]

    def clicar_criar_conta(self):
        self.driver.find_element(By.CLASS_NAME, "login-btn-primary").click()

    def clicar_entrar(self):
        self.driver.find_element(By.CLASS_NAME, "login-btn-secondary").click()

class login_existente_Page:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def abrir(self):
        self.driver.get("http://localhost:8000/login_existente/")

    def obter_titulo(self):
        return self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text

    def obter_botao_voltar(self):
        return self.driver.find_element(By.CLASS_NAME, "back-btn")

    def obter_mensagens_erro(self):
        erros = self.driver.find_elements(By.CLASS_NAME, "error-messages")
        return [e.text for e in erros] if erros else []

    def preencher_login(self, valor):
        campo = self.driver.find_element(By.ID, "id_login")
        campo.clear()
        campo.send_keys(valor)

    def preencher_email(self, valor):
        campo = self.driver.find_element(By.ID, "id_email")
        campo.clear()
        campo.send_keys(valor)

    def preencher_senha(self, valor):
        campo = self.driver.find_element(By.ID, "id_senha")
        campo.clear()
        campo.send_keys(valor)

    def clicar_entrar(self):
        self.driver.find_element(By.CLASS_NAME, "btn-form-submit").click()

