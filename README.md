# RAG-Py-LC-Chroma
RAG-Python-Langchain-ChromaDB ist ein Projekt, das Retrieval-Augmented Generation (RAG) mithilfe von Python, LangChain und ChromaDB umsetzt. 



Hier ist die requirements.txt, die alle notwendigen Python-Pakete enthält. Du kannst diese Datei verwenden, um alle Pakete mit einem einzigen Befehl zu installieren.



Verwendung
	1.	Speichere die Datei als requirements.txt in deinem Projektverzeichnis.
	2.	Stelle sicher, dass du dich in einer virtuellen Umgebung befindest.
	3.	Installiere alle Abhängigkeiten mit:

pip install -r requirements.txt

Optionale Schritte

Falls Tesseract OCR auf System installieren muss, kann man dies separat ausführen.

Dieses Vorgehen sorgt dafür, dass alle benötigten Pakete schnell und konsistent installiert werden. 😊



Um Embedding-Modelle wie Nomic oder Llama 3 8B Instruct zu nutzen, benötigt man zunächst Ollama (offizielle Website). Die Modelle werden mit den folgenden Befehlen bereitgestellt:
	•	Für Nomic Embedding:

ollama pull nomic-embed-text


	•	Für Llama 3 8B Instruct:

ollama pull llama3.1:8b-instruct



Nach dem Herunterladen können die Modelle für Embedding-Generierung oder andere Aufgaben eingesetzt werden.
