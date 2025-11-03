from django.test import TestCase
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pytest, time
from unittest.mock import patch

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
    def test_artigo_sem_banner(self, driver):
        page = exibir_artigo_Page(driver)
        page.abrir("http://localhost:8000/artigo_sem_banner/")
        assert page.obter_titulo() != ""
        assert page.verificar_audio()
        links = page.verificar_links()
        assert "Sugestões de Leitura" in links
        assert "Ver Pontos Chave" in links
        assert not page.verificar_banner()

class Test_home:
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self):
        opts = Options()
        opts.add_argument("--headless")
        self.driver = webdriver.Chrome(options=opts)
        self.driver.get("http://127.0.0.1:8000/")
        yield
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
        msg_vazia = self.driver.find_elements(By.XPATH, "//*[contains(text(),'Não há mais artigos recentes')]")
        assert len(sugestoes) > 0 or len(msg_vazia) > 0

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

class Test_topico_pernambuco:
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self):
        opts = Options()
        opts.add_argument("--headless")
        self.driver = webdriver.Chrome(options=opts)
        self.driver.get("http://127.0.0.1:8000/topico_pernambuco/")
        yield
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
        return self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2"))).text

    def obter_links(self):
        return self.driver.find_elements(By.CSS_SELECTOR, "ul li a")

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
        """
        Testa se a página exibe corretamente a seção 'Entenda o Contexto'
        com os links retornados pela função gerar_contexto().
        """
        mock_gerar_contexto.return_value = {
            "secao": "Entenda o Contexto",
            "links": [
                {
                    "titulo": "História do tema",
                    "url": "https://pt.wikipedia.org/wiki/Exemplo",
                    "descricao": "Explica o contexto histórico do artigo."
                },
                {
                    "titulo": "Análise econômica",
                    "url": "https://exemplo.com/economia",
                    "descricao": "Aborda os impactos econômicos mencionados."
                }
            ]
        }

        # artigo id 1 — deve existir no banco ou você pode criar via fixture ou migration fake
        page = conteudo_contexto_Page(self.driver)
        page.abrir(1)

        titulo = page.obter_titulo()
        assert titulo != ""

        secao = page.obter_secao()
        assert "Entenda o Contexto" in secao

        links = page.obter_links()
        assert len(links) >= 1
        assert any("wikipedia" in l.get_attribute("href") for l in links)

    @patch("app1.views.gerar_contexto")
    def test_sem_links_de_contexto(self, mock_gerar_contexto):
        """
        Testa se a página exibe a mensagem adequada quando não há links.
        """
        mock_gerar_contexto.return_value = {"secao": "", "links": []}

        page = conteudo_contexto_Page(self.driver)
        page.abrir(1)

        assert page.obter_mensagem_vazia()
