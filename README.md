# UniPrep AI 🎓

UniPrep AI est une application web intelligente conçue pour aider les étudiants à réviser leurs cours. Elle utilise l'intelligence artificielle (Google Gemini) et la technique RAG (Retrieval-Augmented Generation) pour permettre aux étudiants de discuter avec leurs documents de cours (PDF).

## Fonctionnalités

*   **Authentification** : Système de connexion et d'inscription pour les étudiants et les administrateurs.
*   **Rôles** :
    *   **Admin** : Peut créer des modules et uploader des fichiers de cours (PDF).
    *   **Étudiant** : Peut sélectionner un module et poser des questions à l'IA sur le contenu du cours.
*   **RAG (Retrieval-Augmented Generation)** : L'IA répond uniquement en se basant sur le contenu des documents fournis, garantissant des réponses pertinentes et fiables.
*   **Base de données** : Utilisation de SQLite pour la gestion des utilisateurs et des modules, et ChromaDB pour le stockage vectoriel des documents.
*   **Interface** : Interface utilisateur intuitive construite avec Streamlit.

## Installation

1.  Cloner le dépôt :
    ```bash
    git clone https://github.com/yassinekamouss/CourseMate-AI.git
    cd CourseMate-AI
    ```

2.  Créer un environnement virtuel et l'activer :
    ```bash
    python3 -m venv env
    source env/bin/activate  # Sur Linux/Mac
    # env\Scripts\activate  # Sur Windows
    ```

3.  Installer les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

4.  Configurer les variables d'environnement :
    Créez un fichier `.env` à la racine du projet et ajoutez votre clé API Google Gemini :
    ```
    GOOGLE_API_KEY=votre_clé_api_ici
    ```

## Utilisation

1.  Lancer l'application :
    ```bash
    streamlit run app.py
    ```

2.  Accéder à l'application dans votre navigateur (généralement à l'adresse `http://localhost:8501`).

## Technologies utilisées

*   Python
*   Streamlit
*   LangChain
*   Google Gemini (via `langchain-google-genai`)
*   ChromaDB
*   SQLite
*   Sentence-Transformers (Embeddings locaux)
