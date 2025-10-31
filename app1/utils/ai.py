from openai import OpenAI
from duckduckgo_search import DDGS
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

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
def gerar_contexto(texto: str) -> dict:
    """
    Gera uma seção 'Entenda o Contexto' com até 3 links de materiais complementares,
    usando o modelo Gemini em modo JSON nativo, com fallback seguro.
    """

    prompt = f"""
Você é um assistente de curadoria de conteúdo jornalístico.  
Analise o texto abaixo e gere uma seção chamada **"Entenda o Contexto"**, que traga até **3 links de materiais complementares** que ajudem o leitor a compreender melhor o tema central do texto.

Os materiais devem:
- Explicar conceitos técnicos, históricos, políticos ou econômicos citados no texto.
- Ser **reais e confiáveis** (portais de notícia, sites do governo, universidades, Wikipedia).
- Ter **URLs verdadeiras** e acessíveis.
- Não repetir o mesmo tipo de material.
- Se não houver material confiável suficiente, gere apenas os que fizerem sentido.

Formato de saída (JSON válido):
{{
  "secao": "Entenda o Contexto",
  "links": [
    {{
      "titulo": "Título descritivo do material",
      "url": "https://exemplo.com/link",
      "descricao": "Breve explicação (1 frase) sobre o que o leitor aprenderá nesse material."
    }}
  ]
}}

Agora analise o texto e gere a resposta conforme o formato acima.

TEXTO:
{texto}
"""

    model = genai.GenerativeModel("models/gemini-2.5-flash")

    try:
        # 🧩 Tenta gerar resposta em formato JSON puro
        resposta = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        conteudo = resposta.text.strip()
        return json.loads(conteudo)

    except Exception as e:
        # ⚠️ Se falhar (modelo não retorna JSON puro ou erro de parsing), tenta limpar
        print("⚠️ Erro no modo JSON nativo:", e)

        # Gera no modo texto normal
        resposta = model.generate_content(prompt)
        conteudo = resposta.text.strip()

        # 🧼 Extrai apenas o bloco JSON se houver texto extra
        match = re.search(r'\{.*\}', conteudo, re.DOTALL)
        conteudo_limpo = match.group(0) if match else conteudo

        try:
            return json.loads(conteudo_limpo)
        except Exception:
            print("⚠️ Resposta não JSON:", conteudo)
            return {
                "secao": "Entenda o Contexto",
                "links": [
                    {
                        "titulo": "Conteúdo não disponível",
                        "url": "",
                        "descricao": "Não foi possível gerar links de contexto."
                    }
                ]
            }