# ingest.py
import os
import time
import pandas as pd
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredHTMLLoader,
    UnstructuredWordDocumentLoader,
)


# Configuração


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY não encontrada no .env")

PASTA_DOCUMENTOS = "documentos"

documents = []


# Leitura dos arquivos


for raiz, _, arquivos in os.walk(PASTA_DOCUMENTOS):

    for arquivo in arquivos:

        caminho = os.path.join(raiz, arquivo)
        ext = os.path.splitext(arquivo)[1].lower()

        try:

            if ext == ".pdf":
                docs = PyPDFLoader(caminho).load()

            elif ext == ".docx":
                docs = UnstructuredWordDocumentLoader(caminho).load()

            elif ext == ".md":
                docs = TextLoader(caminho, encoding="utf-8").load()

            elif ext == ".html":
                docs = UnstructuredHTMLLoader(caminho).load()

            elif ext == ".csv":
                docs = CSVLoader(caminho, encoding="utf-8").load()

            elif ext == ".xlsx":

                docs = []

                planilhas = pd.read_excel(
                    caminho,
                    sheet_name=None
                )

                for aba, df in planilhas.items():

                    docs.append(
                        Document(
                            page_content=df.to_string(index=False),
                            metadata={
                                "aba": aba
                            }
                        )
                    )

            else:
                continue

            departamento = os.path.basename(raiz)

            for doc in docs:
                doc.metadata["arquivo"] = arquivo
                doc.metadata["departamento"] = departamento
                doc.metadata["caminho"] = caminho

            documents.extend(docs)

            print(f"✓ {arquivo}")

        except Exception as e:
            print(f"Erro em {arquivo}: {e}")

print("\n==============================")
print(f"Documentos carregados: {len(documents)}")
print("==============================")


# Chunks


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=200,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)

chunks = splitter.split_documents(documents)

print(f"Trechos criados: {len(chunks)}")


# Embeddings


embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=GOOGLE_API_KEY
)


# Banco vetorial

BATCH_SIZE = 25
PAUSA = 35

vectorstore = None

print("\nCriando banco vetorial...\n")

for inicio in range(0, len(chunks), BATCH_SIZE):

    fim = min(inicio + BATCH_SIZE, len(chunks))

    lote = chunks[inicio:fim]

    print(f"Lote {inicio//BATCH_SIZE + 1} ({inicio+1}-{fim} de {len(chunks)})")

    sucesso = False

    while not sucesso:

        try:

            if vectorstore is None:
                vectorstore = FAISS.from_documents(
                    lote,
                    embeddings
                )
            else:
                vectorstore.add_documents(lote)

            sucesso = True

        except Exception as e:

            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"Limite da API atingido. Aguardando {PAUSA}s...")
                time.sleep(PAUSA)
            else:
                raise

    time.sleep(2)

vectorstore.save_local("vectorstore")

print("\nBase vetorial criada com sucesso!")
