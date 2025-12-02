import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

# Configuration
from langchain_community.embeddings import HuggingFaceEmbeddings

# Configuration
PERSIST_DIRECTORY = "./data/vector_store"

# Utilisation d'un modèle local léger pour les embeddings
EMBEDDING_MODEL = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def process_pdf_and_add_to_vector_db(pdf_file, module_name):
    """Lit un PDF uploadé, le découpe et l'ajoute à la base vectorielle avec le tag du module."""
    
    # 1. Sauvegarde temporaire du fichier pour le lire
    temp_path = f"./temp_{pdf_file.name}"
    with open(temp_path, "wb") as f:
        f.write(pdf_file.getbuffer())
        
    # 2. Chargement et découpage
    loader = PyPDFLoader(temp_path)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    # 3. Ajout des métadonnées (Important pour filtrer par module)
    for split in splits:
        split.metadata['module'] = module_name
        split.metadata['source'] = pdf_file.name

    # 4. Stockage dans ChromaDB
    # Utilisation de PersistentClient pour éviter les erreurs de fichier existant
    import chromadb
    # 4. Stockage dans ChromaDB
    # Utilisation de PersistentClient pour éviter les erreurs de fichier existant
    import chromadb
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    
    # Traitement par lots pour éviter de dépasser les quotas (Rate Limits)
    BATCH_SIZE = 10
    total_splits = len(splits)
    
    for i in range(0, total_splits, BATCH_SIZE):
        batch = splits[i:i + BATCH_SIZE]
        print(f"Traitement du lot {i//BATCH_SIZE + 1}/{(total_splits + BATCH_SIZE - 1)//BATCH_SIZE}")
        
        try:
            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=EMBEDDING_MODEL,
                client=client,
                collection_name="uniprep_collection"
            )
        except Exception as e:
            print(f"Erreur lors du traitement du lot {i}: {e}")
    # vectorstore.persist() # Deprecated in newer versions, auto-persists
    
    # Nettoyage
    os.remove(temp_path)
    return True

def get_qa_chain(module_name):
    """Crée la chaîne de question-réponse filtrée pour un module spécifique."""
    
    import chromadb
    client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    
    vectorstore = Chroma(
        client=client,
        collection_name="uniprep_collection",
        embedding_function=EMBEDDING_MODEL
    )
    
    # Le retriever ne cherche que dans les documents du module choisi
    retriever = vectorstore.as_retriever(
        search_kwargs={'filter': {'module': module_name}, 'k': 5}
    )
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
    
    prompt_template = """Utilise les extraits de cours suivants pour répondre à la question à la fin.
    Si tu ne connais pas la réponse d'après le contexte, dis simplement que ce n'est pas dans le cours.
    
    Contexte: {context}
    
    Question: {question}
    Réponse utile:"""
    
    PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    return qa_chain