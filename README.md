
# **RAG-Py-LC-Chroma**

**RAG-Python-LangChain-ChromaDB** ist ein Projekt, das Retrieval-Augmented Generation (RAG) mithilfe von **Python**, **LangChain** und **ChromaDB** umsetzt. Es bietet eine leistungsstarke Plattform für die Verarbeitung und semantische Suche von Dokumenten.

---

## **Inhalt**

- [Installation](#installation)
- [Verwendung](#verwendung)
- [Optionale Schritte](#optionale-schritte)
- [Embedding-Modelle](#embedding-modelle)

---

## **Installation**

Um die erforderlichen Abhängigkeiten zu installieren, ist eine `requirements.txt`-Datei vorbereitet. Diese enthält alle notwendigen Python-Pakete.

### **Schritte:**
1. Speichere die Datei als `requirements.txt` in deinem Projektverzeichnis.
2. Stelle sicher, dass du dich in einer **virtuellen Umgebung** befindest.
3. Installiere alle Abhängigkeiten mit folgendem Befehl:

   ```bash
   pip install -r requirements.txt

Verwendung
	1.	Starte deine virtuelle Umgebung:

python3 -m venv mein_virtuelles_umfeld
source mein_virtuelles_umfeld/bin/activate  # Für macOS/Linux
mein_virtuelles_umfeld\Scripts\activate     # Für Windows


	2.	Installiere die Abhängigkeiten aus der requirements.txt wie oben beschrieben.
	3.	Starte dein Projekt oder arbeite mit der enthaltenen Funktionalität.

Optionale Schritte

Falls Tesseract OCR auf deinem System benötigt wird, kann dies separat installiert werden:
	•	macOS:

brew install tesseract
brew install tesseract-lang  # Zusätzliche Sprachmodelle


	•	Linux:

sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-deu  # Optional: deutsches Sprachmodell


	•	Windows:
Lade Tesseract von der offiziellen Seite herunter und füge es zur PATH-Umgebungsvariable hinzu.

Embedding-Modelle

Um Embedding-Modelle wie Nomic oder Llama 3 8B Instruct zu nutzen, benötigt man zunächst Ollama. Besuche die offizielle Website, um Ollama herunterzuladen und einzurichten.

Modelle bereitstellen:
	•	Für Nomic Embedding:

ollama pull nomic-embed-text


	•	Für Llama 3 8B Instruct:

ollama pull llama3.1:8b-instruct



Nach dem Herunterladen können die Modelle für Embedding-Generierung oder andere Aufgaben genutzt werden.

Lizenz