import streamlit as st
import os
from packages.rag_engine import process_pdf_and_add_to_vector_db, get_qa_chain
from packages.database import init_db, add_module, get_all_modules
from packages.auth import login_user, register_user, logout_user

# Configuration de la page
st.set_page_config(page_title="UniPrep AI", layout="wide")

# Initialisation de la base de données
init_db()

# --- Gestion de l'authentification ---
if "user" not in st.session_state:
    st.title("🎓 UniPrep AI - Connexion")
    
    tab1, tab2 = st.tabs(["Se connecter", "S'inscrire"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")
            
            if submit:
                if login_user(username, password):
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect.")

    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("Nom d'utilisateur")
            new_pass = st.text_input("Mot de passe", type="password")
            submit_reg = st.form_submit_button("S'inscrire")
            
            if submit_reg:
                if new_user and new_pass:
                    if register_user(new_user, new_pass):
                        st.success("Compte créé ! Vous pouvez vous connecter.")
                    else:
                        st.error("Ce nom d'utilisateur est déjà pris.")
                else:
                    st.error("Veuillez remplir tous les champs.")
    
    st.stop()  # Arrête l'exécution ici si pas connecté

# --- Application Principale ---
user = st.session_state.user
modules = get_all_modules()

# --- Sidebar ---
with st.sidebar:
    st.title("🎓 UniPrep AI")
    st.write(f"Bonjour, **{user['username']}**")
    
    if st.button("Se déconnecter"):
        logout_user()
    
    st.divider()
    
    # Création de nouveau module
    with st.expander("Ajouter un module"):
        new_module = st.text_input("Nom du module")
        if st.button("Créer"):
            if new_module:
                if add_module(new_module):
                    st.success(f"Module {new_module} ajouté !")
                    st.rerun()
                else:
                    st.error("Ce module existe déjà.")
    
    st.divider()

    if modules:
        selected_module = st.selectbox("Choisir un module :", modules)
    else:
        selected_module = None
        st.warning("Aucun module disponible. Créez-en un !")

# --- Interface Principale ---
if selected_module:
    st.header(f"📚 Module : {selected_module}")
    
    # Section Upload (disponible pour tous)
    with st.expander("Importer des cours (PDF)"):
        uploaded_file = st.file_uploader("Choisissez un fichier PDF", type="pdf")
        
        if uploaded_file is not None:
            if st.button("Traiter et Ingérer dans l'IA"):
                with st.spinner("L'IA analyse le document..."):
                    success = process_pdf_and_add_to_vector_db(uploaded_file, selected_module)
                    if success:
                        st.success("Document indexé avec succès ! L'IA est prête.")

    st.divider()
    st.caption("Posez vos questions sur les cours de ce module.")

    # Gestion de l'historique du chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Afficher les messages précédents
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Zone de saisie utilisateur
    if prompt := st.chat_input("Posez votre question..."):
        # Afficher la question utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Générer la réponse
        with st.chat_message("assistant"):
            with st.spinner("Recherche dans le cours..."):
                try:
                    qa_chain = get_qa_chain(selected_module)
                    response = qa_chain.invoke({"query": prompt})
                    answer = response['result']
                    
                    st.markdown(answer)
                    
                    # Optionnel : Afficher les sources
                    with st.expander("Voir les sources utilisées"):
                        for doc in response['source_documents']:
                            st.caption(f"Source: {doc.metadata['source']}")
                            st.text(doc.page_content[:200] + "...")

                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Erreur : {e}")
else:
    st.info("Veuillez sélectionner ou créer un module pour commencer.")
