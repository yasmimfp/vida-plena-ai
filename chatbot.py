import os
from dotenv import load_dotenv

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_community.vectorstores import FAISS


# CONFIGURAÇÕES


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi encontrada.")


# EMBEDDINGS


embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=GOOGLE_API_KEY,
)


# BASE VETORIAL


vectorstore = FAISS.load_local(
    "vectorstore",
    embeddings,
    allow_dangerous_deserialization=True,
)


# MODELO


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.2,
)


# HISTÓRICO


historico = []


def responder(pergunta: str) -> str:
    """Realiza a busca na base vetorial e gera a resposta."""

    documentos = vectorstore.similarity_search(
        pergunta,
        k=4,
    )

    contexto = "\n\n".join(
        doc.page_content for doc in documentos
    )

    conversa = "\n".join(historico[-8:])

    prompt = f"""
Você é o Vida Plena AI, assistente corporativo da empresa Vida Plena S.A.

Sua função é responder dúvidas dos colaboradores utilizando EXCLUSIVAMENTE
as informações presentes na documentação interna da empresa.

=========================
REGRAS
=========================

1. Utilize apenas as informações do contexto recuperado.

2. Nunca invente informações ou complemente respostas com conhecimento próprio.

3. Explique o conteúdo com suas próprias palavras, evitando copiar grandes trechos da documentação.

4. Utilize linguagem profissional, clara, objetiva e cordial.

5. Sempre que fizer sentido, organize a resposta em pequenos parágrafos ou listas.

6. Quando a resposta estiver baseada em uma política, manual, procedimento ou diretriz interna, introduza naturalmente com expressões como:
- "Conforme a política da empresa..."
- "Com base na política interna..."
- "Segundo as diretrizes da empresa..."
- "De acordo com o procedimento interno..."

Escolha a expressão que melhor se encaixar na situação.

7. Nunca mencione nomes de arquivos, extensões (.pdf, .docx, .xlsx, .md, .html) ou detalhes técnicos da implementação.

8. Caso a informação não exista na documentação, responda exatamente:
"Não encontrei essa informação na documentação da empresa."

9. Caso a pergunta não esteja relacionada à documentação interna da empresa, responda:
"Posso ajudar apenas com informações presentes na documentação interna da Vida Plena S.A."

10. Cumprimente, agradeça ou despeça-se naturalmente quando apropriado.

=========================
HISTÓRICO
=========================

{conversa}

=========================
DOCUMENTAÇÃO
=========================

{contexto}

=========================
PERGUNTA
=========================

{pergunta}

=========================
INSTRUÇÃO FINAL
=========================

Escreva uma resposta natural, profissional e objetiva.
Não mencione arquivos ou detalhes técnicos.
Quando apropriado, indique que a resposta está baseada em uma política, procedimento ou diretriz interna da empresa.

Resposta:
"""

    resposta = llm.invoke(prompt).content.strip()

    historico.append(f"Usuário: {pergunta}")
    historico.append(f"Assistente: {resposta}")

    if len(historico) > 20:
        del historico[:-20]

    return resposta
