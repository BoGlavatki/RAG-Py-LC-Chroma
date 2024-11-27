from flask import Flask, render_template, request, jsonify
import logging
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_ollama import ChatOllama
from langchain.retrievers.multi_query import MultiQueryRetriever

from langchain_community.cache import InMemoryCache
import langchain

langchain.cache = None

app = Flask(__name__)

# Logging aktivieren
logging.basicConfig(level=logging.DEBUG)

# Modell und Pfad zur PDF-Datei
local_model = "llama3.1:8b-instruct-q8_0"
llm = ChatOllama(model=local_model)
print("Verwendetes Modell:", llm.model_dump)
local_path = "KI_in_der_Lehre.pdf"

# Lade das PDF und bereite es vor
loader = UnstructuredPDFLoader(file_path=local_path)
data = loader.load()

# Split and chunk
text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
chunks = text_splitter.split_documents(data)

# Add to vector database
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=OllamaEmbeddings(model="nomic-embed-text:latest", show_progress=True),
    collection_name="local-rag"
)

# Multi-query retriever
QUERY_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="""Du bist ein KI-Sprachmodell-Assistent. Deine Aufgabe ist es, fünf verschiedene Versionen der angegebenen Benutzerfrage auf Deutsch zu erstellen, um relevante Dokumente aus einer Vektordatenbank abzurufen. Indem du mehrere Perspektiven auf die Benutzerfrage generierst, sollst du dem Benutzer helfen, einige der Einschränkungen der distanzbasierten Ähnlichkeitssuche zu überwinden. Gib diese alternativen Fragen durch Zeilenumbrüche getrennt aus.
Originalfrage: {question}""",
)

print("************** QUERY_PROMPT--------------------------->", QUERY_PROMPT)

# Angepasste `startSearch`-Funktion
def startSearch(query):
    results = vector_db.similarity_search(query=query, k=3)
    docs = []
    for doc in results:
        print("DOCS:")
        print(f"========================>>>>>>>>>>>* {doc.page_content} [{doc.metadata}]")
        print("END DOCS=========*******************")
        docs.append(doc)
    return docs  # Dokumente zurückgeben

retriever = MultiQueryRetriever.from_llm(
    vector_db.as_retriever(search_kwargs={"k": 10}),
    llm,
    prompt=QUERY_PROMPT
)

# RAG prompt
template = """
Bitte beantworte die folgende Frage ausschließlich auf Deutsch, basierend auf dem bereitgestellten Kontext. Deine Antwort soll detailliert und umfassend sein, und sich ausschließlich auf den bereitgestellten Kontext stützen.

**Kontext:**
{context}

**Frage:**
{question}

**Antwort:**
"""

prompt = ChatPromptTemplate.from_template(template)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if request.is_json:
            user_input = request.json.get('user_input')
        else:
            user_input = request.form.get('user_input')
        
        if not user_input:
            raise ValueError("No user input provided")
        
        logging.debug(f"User input: {user_input}")

        # Ergebnisse aus `startSearch` abrufen
        search_docs = startSearch(user_input)
        print("Retriev from startSearch: \n" + search_docs)

        # Ergebnisse aus `retriever` abrufen
        retrieved_docs = retriever.get_relevant_documents(user_input)

        # Kombination der Ergebnisse (Duplikate entfernen)
        all_docs = search_docs + retrieved_docs
        unique_docs = {doc.page_content: doc for doc in all_docs}.values()  # Entferne Duplikate basierend auf Inhalten

        # Begrenze auf die relevantesten Dokumente
        top_docs = list(unique_docs)[:5]  # Maximal 5 relevante Dokumente
        context = "\n".join([doc.page_content for doc in top_docs])

        logging.debug(f"Combined context: {context}")

        # Antwort vom LLM generieren
        response = llm.invoke(prompt.format(context=context, question=user_input))
        response_text = response.content if hasattr(response, 'content') else str(response)

        logging.debug(f"LLM response: {response_text}")
        
        return jsonify({'response': response_text})
    except Exception as e:
        logging.error(f"Error during chat processing: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
