import os
import json
import streamlit as st
from dotenv import load_dotenv

import importlib
# Load local pipeline components
import rag_pipeline
import llm_manager
import styles

# Reload trigger: 1
importlib.reload(styles)
importlib.reload(rag_pipeline)
importlib.reload(llm_manager)

# Load local environment variables from .env
load_dotenv()

# Streamlit Page Configuration (Collapse sidebar by default)
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constants
STORE_DIR = "vector_store_db"
STATS_FILE = os.path.join(STORE_DIR, "doc_stats.json")

# Injects premium CSS styling (includes sidebar-hiding styles)
st.markdown(styles.get_css(), unsafe_allow_html=True)

# Centered Project Name Header
st.markdown(
    """
    <div style="text-align: center; margin-top: 0px; margin-bottom: 0.5rem;">
        <span style="font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #e25c38 0%, #f43f5e 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 0.05em;">
            🎓 AI STUDY ASSISTANT
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processed_files" not in st.session_state:
    st.session_state.processed_files = []
if "stats" not in st.session_state:
    st.session_state.stats = {"total_files": 0, "total_pages": 0, "total_chunks": 0}
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "summary_content" not in st.session_state:
    st.session_state.summary_content = ""
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_feedback" not in st.session_state:
    st.session_state.quiz_feedback = {}
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []
if "flashcard_index" not in st.session_state:
    st.session_state.flashcard_index = 0
if "flashcard_revealed" not in st.session_state:
    st.session_state.flashcard_revealed = False
if "custom_uploaded_files" not in st.session_state:
    st.session_state.custom_uploaded_files = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# Helper to format file size human-readably
def format_size(bytes_size):
    if bytes_size == 0:
        return "Indexed"
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"

# Resolve active API key
active_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""

# -------------------------------------------------------------
# AUTO-LOAD EXISTING DATABASE ON STARTUP
# -------------------------------------------------------------
if st.session_state.vector_store is None:
    try:
        embeddings = rag_pipeline.get_embeddings_model(use_google=False)
        vector_store = rag_pipeline.load_vector_store(embeddings, STORE_DIR)
        if vector_store:
            st.session_state.vector_store = vector_store
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, "r") as f:
                    data = json.load(f)
                    st.session_state.processed_files = data.get("files", [])
                    st.session_state.stats = data.get("stats", st.session_state.stats)
                    # Pre-populate custom file list
                    if not st.session_state.custom_uploaded_files:
                        for filename in st.session_state.processed_files:
                            st.session_state.custom_uploaded_files.append({
                                "name": filename,
                                "size": 0,
                                "file": None
                            })
    except Exception as e:
        print(f"Error auto-loading database: {e}")

# -------------------------------------------------------------
# MAIN APP 2-COLUMN LAYOUT
# -------------------------------------------------------------
col_left, col_right = st.columns([1.1, 2.0], gap="large")

# =============================================================
# LEFT COLUMN: TITLE & ACTIVE MATERIALS
# =============================================================
with col_left:
    st.markdown(
        """
        <div style="margin-top: 0.25rem;">
            <h1 style="font-family: 'Outfit', sans-serif; font-size: 2.8rem; font-weight: 800; color: #1e293b; line-height: 1.15; margin-bottom: 0.75rem;">
                Don't Let Hard Concepts <br><span style="color: #e25c38;">Kill Your Grades.</span>
            </h1>
            <p style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.98rem; color: #64748b; line-height: 1.6; margin-bottom: 1rem;">
                Upload lecture slides, notes, textbooks, or other documents. Instantly interrogate notes using grounded search, test recall accuracy with quizzes, or prepare with mock interview questions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Rounded Pill Badges
    st.markdown(
        """
        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.25rem;">
            <span class="badge-item">Free to use</span>
            <span class="badge-item">Context Grounded</span>
            <span class="badge-item">Auto-Graded Quizzes</span>
            <span class="badge-item">Interview Prep</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Active Materials Section
    st.markdown(
        """
        <p style="font-size: 0.75rem; font-weight: 700; color: #e25c38; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.75rem; font-family: 'Outfit';">
            📄 Active Materials
        </p>
        """,
        unsafe_allow_html=True
    )
    
    if not st.session_state.processed_files:
        st.markdown(
            """
            <div style="background: #ffffff; border: 1px dashed #cbd5e1; border-radius: 12px; padding: 1.5rem; text-align: center; color: #94a3b8; font-size: 0.9rem; font-family: 'Plus Jakarta Sans';">
                No active study materials. Upload slides or notes in Step 01 to start.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        active_materials_html = "<div style='display: flex; flex-direction: column; gap: 8px;'>"
        for filename in st.session_state.processed_files:
            active_materials_html += f"""
            <div class="doc-card">
                <span style="font-size: 1.5rem;">📄</span>
                <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; width: 100%;">
                    <div style="font-size: 0.88rem; font-weight: 600; color: #1e293b; font-family: 'Plus Jakarta Sans'; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{filename}</div>
                    <div style="font-size: 0.75rem; color: #64748b; font-family: 'Plus Jakarta Sans';">Type: Document</div>
                </div>
            </div>
            """
        active_materials_html += "</div>"
        st.markdown(active_materials_html, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Active Materials", key="clear_all_materials", use_container_width=True):
            if os.path.exists(STORE_DIR):
                import shutil
                for i in range(3):
                    try:
                        shutil.rmtree(STORE_DIR)
                        break
                    except Exception:
                        import time
                        time.sleep(0.5)
            st.session_state.vector_store = None
            st.session_state.processed_files = []
            st.session_state.stats = {"total_files": 0, "total_pages": 0, "total_chunks": 0}
            st.session_state.chat_history = []
            st.session_state.summary_content = ""
            st.session_state.quiz_questions = []
            st.session_state.flashcards = []
            st.session_state.custom_uploaded_files = []
            st.session_state.uploader_key = 0
            st.success("Database cleared!")
            st.rerun()

# =============================================================
# RIGHT COLUMN: STEPS & STUDY MODE PANEL
# =============================================================
with col_right:
    # CARD 01: UPLOAD MATERIALS
    with st.container(border=True):
        # Custom upload marker to apply the dark theme CSS to this container
        upload_state_class = "empty-state" if not st.session_state.custom_uploaded_files else "has-files-state"
        st.markdown(f'<span class="custom-upload-marker {upload_state_class}"></span>', unsafe_allow_html=True)
        
        st.markdown(
            """
            <div class="step-header">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.25rem;">
                    <span style="font-size: 1.4rem;">📄</span>
                    <span style="font-size: 1.25rem; font-weight: 700; color: #1e293b; font-family: 'Outfit';">Upload PDF</span>
                </div>
            </div>
            <p style="font-size: 0.9rem; color: #64748b; margin-bottom: 0.75rem; font-family: 'Plus Jakarta Sans'; font-weight: 500;">
                Choose a PDF
            </p>
            """,
            unsafe_allow_html=True
        )
        
        # Display uploaded file list inside the container
        if st.session_state.custom_uploaded_files:
            for idx, f_info in enumerate(st.session_state.custom_uploaded_files):
                card_cols = st.columns([12, 1], gap="small")
                with card_cols[0]:
                    st.markdown(
                        f"""
                        <div class="custom-file-card">
                            <div class="file-icon-wrapper">
                                <span>📄</span>
                            </div>
                            <div class="file-details">
                                <div class="file-name">{f_info['name']}</div>
                                <div class="file-size">{format_size(f_info['size'])}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with card_cols[1]:
                    if st.button("ⓧ", key=f"btn_del_file_{idx}_{st.session_state.uploader_key}"):
                        deleted_file = st.session_state.custom_uploaded_files.pop(idx)
                        
                        # If the deleted file was already processed, clean it up from vector store
                        if deleted_file["name"] in st.session_state.processed_files:
                            db = st.session_state.vector_store
                            if db:
                                ids_to_delete = [
                                    doc_id for doc_id, doc in db.docstore._dict.items()
                                    if doc.metadata.get("source") == deleted_file["name"]
                                ]
                                if ids_to_delete:
                                    # Find pages deleted
                                    deleted_pages = 0
                                    for doc_id in ids_to_delete:
                                        doc = db.docstore._dict.get(doc_id)
                                        if doc:
                                            deleted_pages = doc.metadata.get("total_pages", 0)
                                            break
                                    
                                    db.delete(ids_to_delete)
                                    db.save_local(STORE_DIR)
                                    
                                    # Update stats
                                    st.session_state.stats["total_files"] = max(0, st.session_state.stats["total_files"] - 1)
                                    st.session_state.stats["total_pages"] = max(0, st.session_state.stats["total_pages"] - deleted_pages)
                                    st.session_state.stats["total_chunks"] = max(0, st.session_state.stats["total_chunks"] - len(ids_to_delete))
                            
                            # Remove from processed files
                            st.session_state.processed_files.remove(deleted_file["name"])
                            
                            # Save stats or clear entirely if empty
                            if not st.session_state.processed_files:
                                if os.path.exists(STORE_DIR):
                                    import shutil
                                    for i in range(3):
                                        try:
                                            shutil.rmtree(STORE_DIR)
                                            break
                                        except Exception:
                                            import time
                                            time.sleep(0.5)
                                st.session_state.vector_store = None
                                st.session_state.stats = {"total_files": 0, "total_pages": 0, "total_chunks": 0}
                                if os.path.exists(STATS_FILE):
                                    os.remove(STATS_FILE)
                            else:
                                with open(STATS_FILE, "w") as f:
                                    json.dump({
                                        "files": st.session_state.processed_files,
                                        "stats": st.session_state.stats
                                    }, f)
                                    
                        st.rerun()

        # Render file uploader widget
        uploader_key = f"pdf_uploader_widget_{st.session_state.uploader_key}"
        uploaded_pdfs = st.file_uploader(
            "Upload Study Materials (PDFs)",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=uploader_key
        )
        
        # Check for new file uploads and append them
        if uploaded_pdfs:
            new_files_added = False
            for f in uploaded_pdfs:
                if not any(exist_f["name"] == f.name for exist_f in st.session_state.custom_uploaded_files):
                    st.session_state.custom_uploaded_files.append({
                        "name": f.name,
                        "size": f.size,
                        "file": f
                    })
                    new_files_added = True
            
            if new_files_added:
                st.session_state.uploader_key += 1
                st.rerun()
                
        # Caption below button when empty
        if not st.session_state.custom_uploaded_files:
            st.markdown('<div class="upload-caption">200MB per file • PDF</div>', unsafe_allow_html=True)
            
        # Action button
        process_btn = st.button("Process PDF", key="btn_process_docs", use_container_width=True)
            
        if process_btn:
            if not st.session_state.custom_uploaded_files:
                st.warning("⚠️ Please choose at least one PDF file to upload.")
            elif not active_api_key or active_api_key == "your_gemini_api_key_here":
                st.error("🔑 Gemini API key not found. Please add your `GOOGLE_API_KEY` in the `.env` file.")
            else:
                # Get files that are not yet processed
                new_files = [f for f in st.session_state.custom_uploaded_files if f["file"] is not None]
                
                if not new_files:
                    st.info("ℹ️ All documents are already processed and indexed.")
                else:
                    with st.spinner("Extracting text and chunking PDFs..."):
                        raw_docs = rag_pipeline.extract_text_from_pdfs([f["file"] for f in new_files])
                        if not raw_docs:
                            st.error("Could not extract text from the uploaded PDFs. Please make sure they are not scanned/image-only PDFs.")
                        else:
                            chunks = rag_pipeline.chunk_documents(raw_docs)
                            with st.spinner("Building FAISS index..."):
                                embeddings = rag_pipeline.get_embeddings_model(use_google=False)
                                
                                if st.session_state.vector_store is None:
                                    v_store = rag_pipeline.build_vector_store(chunks, embeddings, STORE_DIR)
                                    if v_store:
                                        st.session_state.vector_store = v_store
                                else:
                                    st.session_state.vector_store.add_documents(chunks)
                                    st.session_state.vector_store.save_local(STORE_DIR)
                                
                                # Update list of processed files
                                for f in new_files:
                                    if f["name"] not in st.session_state.processed_files:
                                        st.session_state.processed_files.append(f["name"])
                                
                                # Stats compilation
                                unique_files_pages = {}
                                for d in raw_docs:
                                    f_name = d.metadata.get("source")
                                    f_pages = d.metadata.get("total_pages", 1)
                                    unique_files_pages[f_name] = f_pages
                                new_pages = sum(unique_files_pages.values())
                                
                                st.session_state.stats["total_files"] = len(st.session_state.processed_files)
                                st.session_state.stats["total_pages"] += new_pages
                                st.session_state.stats["total_chunks"] += len(chunks)
                                
                                # Mark as indexed
                                for f in st.session_state.custom_uploaded_files:
                                    f["file"] = None
                                    
                                with open(STATS_FILE, "w") as f:
                                    json.dump({
                                        "files": st.session_state.processed_files,
                                        "stats": st.session_state.stats
                                    }, f)
                                    
                                st.rerun()
                                
        # Display ready banner if vector store is populated and files match
        files_indexed = st.session_state.processed_files
        custom_files = [f["name"] for f in st.session_state.custom_uploaded_files]
        is_ready = (
            st.session_state.vector_store is not None 
            and len(custom_files) > 0 
            and all(name in files_indexed for name in custom_files)
        )
        if is_ready:
            st.markdown('<div class="pdf-ready-banner">PDF Ready!</div>', unsafe_allow_html=True)
                                

    
    # CARD 02: SELECT STUDY MODE
    with st.container(border=True):
        st.markdown(
            """
            <div class="step-header">
                <div class="step-badge">02</div>
                <div class="step-title">Select active study mode</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        study_mode = st.selectbox(
            "Select active study mode",
            options=["Study Chatbot", "Document Summarizer", "Flashcards", "Practice Quiz"],
            label_visibility="collapsed",
            key="selectbox_study_mode"
        )
        

    
    # CARD 03: STUDY MODE PANEL DISPLAY
    with st.container(border=True):
        # 1. API key verification
        if not active_api_key or active_api_key == "your_gemini_api_key_here":
            st.warning("🔑 Google Gemini API key not configured. Please set the `GOOGLE_API_KEY` inside the `.env` file in the project folder to enable study modes.")
        # 2. Vector DB check
        elif not st.session_state.vector_store:
            st.info("💡 No active study materials indexed. Please upload your study documents in Step 01 to initialize the AI.")
        else:
            # Render selected module
            if study_mode == "Study Chatbot":
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.25rem;">
                        <span style="font-size: 1.4rem;">💬</span>
                        <span style="font-size: 1.25rem; font-weight: 700; color: #1e293b; font-family: 'Outfit';">Study Chatbot</span>
                    </div>
                    <p style="font-size: 0.9rem; color: #64748b; margin-bottom: 1.25rem; font-family: 'Plus Jakarta Sans';">
                        Ask questions strictly grounded in your active notes. Footnote citations are shown below answers.
                    </p>
                    """,
                    unsafe_allow_html=True
                )
                
                # Chat message logs
                for msg in st.session_state.chat_history:
                    role = msg["role"]
                    content = msg["content"]
                    citations = msg.get("citations", [])
                    
                    if role == "user":
                        st.markdown(
                            f"""
                            <div style="background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 12px 12px 0 12px; padding: 12px; margin-bottom: 10px; width: fit-content; max-width: 85%; margin-left: auto; font-family: 'Plus Jakarta Sans'; font-size: 0.95rem; color:#1e293b;">
                                {content}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px 12px 12px 0; padding: 12px; margin-bottom: 10px; width: fit-content; max-width: 85%; font-family: 'Plus Jakarta Sans'; font-size: 0.95rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02); color:#1e293b;">
                                <strong>Tutor:</strong><br>{content}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Add reader button next to response
                        st.components.v1.html(styles.get_voice_output_html(content), height=45)
                        
                        if citations:
                            with st.expander("🔍 Citations & Sources"):
                                for cite in citations:
                                    st.markdown(
                                        f"**[Source {cite['id']}]** `File: {cite['source']}` (Page {cite['page']})\n"
                                        f"> *\"{cite['content'][:220]}...\"*"
                                    )
                                    
                # Microphone voice dictate widget
                st.components.v1.html(styles.get_voice_input_html(), height=60)
                
                # Text input
                user_query = st.chat_input("Ask a question about your files...")
                if user_query:
                    st.session_state.chat_history.append({"role": "user", "content": user_query})
                    try:
                        llm = llm_manager.get_llm(active_api_key)
                        context_chunks = rag_pipeline.search_documents(st.session_state.vector_store, user_query, k=4)
                        
                        with st.spinner("Thinking..."):
                            answer, citations = llm_manager.answer_question(
                                llm=llm,
                                query=user_query,
                                context_chunks=context_chunks,
                                chat_history=st.session_state.chat_history[:-1]
                            )
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": answer,
                                "citations": citations
                            })
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error answering query: {e}")
                        
            elif study_mode == "Document Summarizer":
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.25rem;">
                        <span style="font-size: 1.4rem;">📋</span>
                        <span style="font-size: 1.25rem; font-weight: 700; color: #1e293b; font-family: 'Outfit';">Document Summarizer</span>
                    </div>
                    <p style="font-size: 0.9rem; color: #64748b; margin-bottom: 1.25rem; font-family: 'Plus Jakarta Sans';">
                        Generate and download comprehensive study guides from your material.
                    </p>
                    """,
                    unsafe_allow_html=True
                )
                
                sum_cols = st.columns([1, 1])
                with sum_cols[0]:
                    gen_btn = st.button("Generate Summary", key="btn_gen_summary", use_container_width=True)
                with sum_cols[1]:
                    if st.session_state.summary_content:
                        st.download_button(
                            label="📥 Download Study Guide",
                            data=st.session_state.summary_content,
                            file_name="Study_Guide.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                        
                if gen_btn:
                    with st.spinner("Drafting guide..."):
                        try:
                            all_docs = [
                                st.session_state.vector_store.docstore.search(idx)
                                for idx in st.session_state.vector_store.index_to_docstore_id.values()
                            ]
                            llm = llm_manager.get_llm(active_api_key)
                            summary = llm_manager.generate_summary(llm, all_docs)
                            st.session_state.summary_content = summary
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error compiling summary: {e}")
                            
                if st.session_state.summary_content:
                    st.markdown("---")
                    st.markdown(st.session_state.summary_content)
                    
            elif study_mode == "Flashcards":
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.25rem;">
                        <span style="font-size: 1.4rem;">🧠</span>
                        <span style="font-size: 1.25rem; font-weight: 700; color: #1e293b; font-family: 'Outfit';">Interactive Flashcards</span>
                    </div>
                    <p style="font-size: 0.9rem; color: #64748b; margin-bottom: 1.25rem; font-family: 'Plus Jakarta Sans';">
                        Flip through interactive cards generated from key document terms.
                    </p>
                    """,
                    unsafe_allow_html=True
                )
                
                config_cols = st.columns([2, 1])
                with config_cols[0]:
                    num_cards_val = st.slider("Deck Size", min_value=3, max_value=12, value=5, step=1, key="flashcard_deck_size")
                with config_cols[1]:
                    gen_fc_btn = st.button("Generate Cards", key="btn_gen_flashcards", use_container_width=True)
                    
                if gen_fc_btn:
                    with st.spinner("Creating cards..."):
                        try:
                            all_docs = [
                                st.session_state.vector_store.docstore.search(idx)
                                for idx in st.session_state.vector_store.index_to_docstore_id.values()
                            ]
                            llm = llm_manager.get_llm(active_api_key)
                            cards = llm_manager.generate_flashcards(llm, all_docs, num_cards_val)
                            st.session_state.flashcards = cards
                            st.session_state.flashcard_index = 0
                            st.session_state.flashcard_revealed = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error generating flashcards: {e}")
                            
                if st.session_state.flashcards:
                    fc = st.session_state.flashcards[st.session_state.flashcard_index]
                    role_label = "BACK (ANSWER)" if st.session_state.flashcard_revealed else "FRONT (CONCEPT)"
                    content_label = fc["back"] if st.session_state.flashcard_revealed else fc["front"]
                    
                    st.markdown(
                        f"""
                        <div class="flashcard">
                            <div class="flashcard-role">{role_label}</div>
                            <div class="flashcard-content">{content_label}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    fc_ctrls = st.columns([1, 2, 2, 1])
                    with fc_ctrls[0]:
                        if st.button("⬅️", disabled=(st.session_state.flashcard_index == 0), key="btn_prev_card", use_container_width=True):
                            st.session_state.flashcard_index -= 1
                            st.session_state.flashcard_revealed = False
                            st.rerun()
                    with fc_ctrls[1]:
                        reveal_label = "👁️ Hide Answer" if st.session_state.flashcard_revealed else "🎯 Reveal Answer"
                        if st.button(reveal_label, key="btn_reveal_card", use_container_width=True):
                            st.session_state.flashcard_revealed = not st.session_state.flashcard_revealed
                            st.rerun()
                    with fc_ctrls[2]:
                        st.components.v1.html(styles.get_voice_output_html(content_label), height=45)
                    with fc_ctrls[3]:
                        if st.button("➡️", disabled=(st.session_state.flashcard_index == len(st.session_state.flashcards) - 1), key="btn_next_card", use_container_width=True):
                            st.session_state.flashcard_index += 1
                            st.session_state.flashcard_revealed = False
                            st.rerun()
                            
                    st.markdown(f"<p style='text-align: center; color: #94a3b8; font-size: 0.85rem; margin-top: 10px;'>Card {st.session_state.flashcard_index + 1} of {len(st.session_state.flashcards)}</p>", unsafe_allow_html=True)
                    
            elif study_mode == "Practice Quiz":
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.25rem;">
                        <span style="font-size: 1.4rem;">📝</span>
                        <span style="font-size: 1.25rem; font-weight: 700; color: #1e293b; font-family: 'Outfit';">Practice Quiz</span>
                    </div>
                    <p style="font-size: 0.9rem; color: #64748b; margin-bottom: 1.25rem; font-family: 'Plus Jakarta Sans';">
                        Challenge yourself with interactive multiple choice questions and detailed explanations.
                    </p>
                    """,
                    unsafe_allow_html=True
                )
                
                config_cols = st.columns([2, 1])
                with config_cols[0]:
                    num_questions = st.slider("Questions", min_value=3, max_value=10, value=5, key="quiz_questions_count")
                with config_cols[1]:
                    gen_qz_btn = st.button("Generate Quiz", key="btn_gen_quiz", use_container_width=True)
                    
                if gen_qz_btn:
                    with st.spinner("Drafting quiz..."):
                        try:
                            all_docs = [
                                st.session_state.vector_store.docstore.search(idx)
                                for idx in st.session_state.vector_store.index_to_docstore_id.values()
                            ]
                            llm = llm_manager.get_llm(active_api_key)
                            quiz = llm_manager.generate_quiz(llm, all_docs, num_questions)
                            st.session_state.quiz_questions = quiz
                            st.session_state.quiz_answers = {}
                            st.session_state.quiz_feedback = {}
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error generating quiz: {e}")
                            
                if st.session_state.quiz_questions:
                    score = 0
                    total_answered = 0
                    for idx, q in enumerate(st.session_state.quiz_questions):
                        st.markdown(
                            f"""
                            <div class="quiz-card">
                                <div class="quiz-question">Question {idx+1}: {q['question']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        selected_ans = st.radio(
                            "Select option:",
                            options=q["options"],
                            key=f"radio_quiz_{idx}",
                            index=None if f"radio_quiz_{idx}" not in st.session_state.quiz_answers else q["options"].index(st.session_state.quiz_answers[f"radio_quiz_{idx}"])
                        )
                        
                        check_btn = st.button("Check Answer", key=f"btn_quiz_{idx}")
                        is_submitted = f"btn_quiz_{idx}" in st.session_state.quiz_feedback
                        
                        if check_btn or is_submitted:
                            if selected_ans is None:
                                st.warning("⚠️ Please choose an option.")
                            else:
                                st.session_state.quiz_answers[f"radio_quiz_{idx}"] = selected_ans
                                st.session_state.quiz_feedback[f"btn_quiz_{idx}"] = True
                                
                                is_correct = selected_ans == q["answer"]
                                if is_correct:
                                    st.success("🎉 Correct!")
                                else:
                                    st.error(f"❌ Incorrect. Correct answer: **{q['answer']}**")
                                st.info(f"💡 **Explanation:** {q['explanation']}")
                                
                        if f"btn_quiz_{idx}" in st.session_state.quiz_feedback:
                            total_answered += 1
                            if st.session_state.quiz_answers.get(f"radio_quiz_{idx}") == q["answer"]:
                                score += 1
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                    if total_answered == len(st.session_state.quiz_questions):
                        st.markdown("---")
                        st.markdown(f"#### 📊 Result: **{score} / {len(st.session_state.quiz_questions)}**")
                        if score == len(st.session_state.quiz_questions):
                            st.balloons()
                        if st.button("Reset Quiz", key="btn_reset_quiz", use_container_width=True):
                            st.session_state.quiz_answers = {}
                            st.session_state.quiz_feedback = {}
                            st.rerun()
