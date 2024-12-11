from flask import Flask, render_template, request, jsonify
import logging
import os
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_ollama import ChatOllama
from langchain.retrievers.multi_query import MultiQueryRetriever
import json
from langchain_community.cache import InMemoryCache
import langchain

# Erstelle ein Verzeichnis für hochgeladene Dateien
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Bestehender Code bleibt erhalten...

# Liste der hochgeladenen PDFs
uploaded_files = []

langchain.cache = None

app = Flask(__name__)

# Logging aktivieren
logging.basicConfig(level=logging.DEBUG)

# Modell und Pfad zur PDF-Datei
local_model = "llama3.1:8b-instruct-q8_0"
llm = ChatOllama(model=local_model)
llm.temperature = 0.7
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
    results = vector_db.similarity_search(query=query, k=5)
    docs = []
    for doc in results:
        print("DOCS:")
        print(f"========================>>>>>>>>>>>* {doc.page_content} [{doc.metadata}]")
        print("END DOCS=========*******************")
        docs.append(doc)
    return docs  # Dokumente zurückgeben

retriever = MultiQueryRetriever.from_llm(
    vector_db.as_retriever(search_kwargs={"k": 5}),
    llm,
    prompt=QUERY_PROMPT
)

# RAG prompt
template = """
Bitte beantworte die folgende Frage ausschließlich auf Deutsch, basierend auf dem bereitgestellten Kontext. Gib eine kurze Antwort. Halte deine Antwort strikt auf maximal 200 Wörter begrenzt.
 Deine Antwort soll detailliert und umfassend sein, und sich ausschließlich auf den bereitgestellten Kontext stützen.

**Kontext:**
{context}

**Frage:**
{question}

**Antwort:**
"""

prompt = ChatPromptTemplate.from_template(template)


@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({'success': False, 'error': 'No file part in the request'}), 400
        
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected for uploading'}), 400
        
        # Speichere die Datei
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        uploaded_files.append(file.filename)

        # Verarbeite die hochgeladene Datei (ähnlich wie bei `local_path`)
        loader = UnstructuredPDFLoader(file_path=file_path)
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
        chunks = text_splitter.split_documents(data)
        
        # Füge die Chunks zur Vektordatenbank hinzu
        vector_db.add_documents(documents=chunks)

        logging.info(f"File {file.filename} uploaded and added to vector database successfully.")

        return jsonify({'success': True, 'filename': file.filename})
    except Exception as e:
        logging.error(f"Error during file upload: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get_uploaded_files', methods=['GET'])
def get_uploaded_files():
    return jsonify({'uploaded_files': uploaded_files})

@app.route('/uploaded_files', methods=['GET'])
def get_uploaded_files_list():
    try:
        # Dateien aus dem Upload-Ordner lesen
        files = os.listdir(UPLOAD_FOLDER)
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        logging.error(f"Error reading uploaded files: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/delete_file', methods=['POST'])
def delete_file():
    try:
        data = request.json
        filename = data.get('filename')

        if not filename:
            return jsonify({'success': False, 'error': 'No filename provided'}), 400

        # Pfad zur Datei im Upload-Ordner
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        print("File PATH ::: file_path")
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404

        # Datei löschen
        os.remove(file_path)
        return jsonify({'success': True, 'message': f'File {filename} deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/')
def index():
    try:
        # Dateien aus dem Upload-Ordner lesen
        files = os.listdir(UPLOAD_FOLDER)
        files = [file for file in files if os.path.isfile(os.path.join(UPLOAD_FOLDER, file))]  # Nur Dateien
        return render_template('index.html', uploaded_files=files)
    except Exception as e:
        logging.error(f"Error reading uploaded files: {e}")
        return render_template('index.html', uploaded_files=[])

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
        print("Retriev from startSearch: \n" + str(search_docs))

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


