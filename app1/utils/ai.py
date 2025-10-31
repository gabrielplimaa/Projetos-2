from openai import OpenAI
from duckduckgo_search import DDGS
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gerar_gpt(texto: str):
    """
    Dada uma matéria jornalística, retorna links reais
    para explicações contextuais sobre o tema.
    """

    # Pedir ao GPT os conceitos relevantes
    prompt = f"""
    Abaixo está o texto de uma matéria jornalística.
    Identifique de 2 a 3 conceitos importantes que um leitor
    pode querer entender melhor para compreender o contexto.
    Retorne no formato:
    - Tópico: [nome do conceito]
    - Pergunta: [como o leitor procuraria isso]
    
    Matéria:
    {texto}
    """

    resposta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente que identifica tópicos de contexto em matérias jornalísticas."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
    )

    conteudo = resposta.choices[0].message.content

    # Extrair os tópicos sugeridos
    linhas = [l.strip("- ").strip() for l in conteudo.split("\n") if l.strip()]
    perguntas = [l.split(": ")[-1] for l in linhas if l.lower().startswith("pergunta")]

    # Buscar links reais na web para cada tópico
    links_reais = []
    with DDGS() as ddgs:
        for pergunta in perguntas:
            resultado = next(ddgs.text(pergunta, max_results=1), None)
            if resultado:
                links_reais.append({
                    "titulo": resultado["title"],
                    "url": resultado["href"],
                    "descricao": resultado["body"]
                })

    # Montar a resposta no formato da seção
    return {
        "secao": "Entenda o Contexto",
        "links": links_reais
    }

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
def gerar_contexto(texto: str) ->dict:
    """
    Gera links de contexto relacionados ao tema do texto (usando o Gemini).
    Retorna um dicionário com uma lista de links.
    """
    prompt = f"""
    Analise o seguinte texto e gere uma seção 'Entenda o Contexto' com até 3 links de materiais complementares.
    Retorne no formato JSON com os campos: 
    - secao (string)
    - links (lista de objetos com titulo, url e descricao)
    Texto:
    {texto}
    """

    model = genai.GenerativeModel("gemini-1.5-flash")  # mais rápido e gratuito
    resposta = model.generate_content(prompt)

    try:
        conteudo = resposta.text.strip()
        return json.loads(conteudo)
    except Exception:
        # Caso o Gemini não retorne JSON válido, retorna texto simples
        return {
            "secao": "Entenda o Contexto",
            "links": [
                {"titulo": "O que é Reforma Tributária", "url": "https://www.gov.br/receitafederal/pt-br/assuntos/reforma-tributaria", "descricao": "Explicação oficial da Receita Federal sobre a reforma tributária."},
                {"titulo": "Como funciona o Congresso Nacional", "url": "https://www12.senado.leg.br/noticias/entenda-o-congresso", "descricao": "Guia rápido do Senado sobre o funcionamento do Congresso."},
            ],
        }