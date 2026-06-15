import os
import shutil
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# Absolute imports for embeddings to support both local and API options
from langchain_huggingface import HuggingFaceEmbeddings

def extract_text_from_pdfs(pdf_files):
    """
    Extracts text page-by-page from multiple uploaded PDF files.
    Each extracted page is mapped into a Document object preserving metadata (filename, page number).
    
    Args:
        pdf_files: List of file-like objects (e.g., UploadedFile from Streamlit)
        
    Returns:
        List of Document objects representing individual pages.
    """
    documents = []
    
    for pdf_file in pdf_files:
        # If it's a Streamlit UploadedFile, it has a name attribute. Otherwise, use filename.
        filename = getattr(pdf_file, 'name', 'Uploaded Document')
        
        try:
            reader = PdfReader(pdf_file)
            total_pages = len(reader.pages)
            
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    doc = Document(
                        page_content=page_text.strip(),
                        metadata={
                            "source": filename,
                            "page": idx + 1,
                            "total_pages": total_pages
                        }
                    )
                    documents.append(doc)
        except Exception as e:
            print(f"Error reading PDF file {filename}: {e}")
            
    return documents

def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
    """
    Splits the extracted document pages into smaller, overlapping chunks for optimal embedding.
    
    Args:
        documents: List of Document objects
        chunk_size: Target characters per chunk
        chunk_overlap: Overlapping characters between adjacent chunks
        
    Returns:
        List of split Document chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return text_splitter.split_documents(documents)

def get_embeddings_model(use_google=False, google_api_key=None):
    """
    Retrieves the embedding model. Supports local HuggingFace embeddings or Google Gemini Embeddings.
    
    Args:
        use_google: Boolean indicating whether to use Google Gemini Embeddings
        google_api_key: Optional API key for Google Gemini
        
    Returns:
        An instance of an Embeddings class (HuggingFaceEmbeddings or GoogleGenerativeAIEmbeddings).
    """
    if use_google and google_api_key:
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=google_api_key
            )
        except Exception as e:
            print(f"Error initializing Google Embeddings, falling back to local: {e}")
            
    # Fallback to local HuggingFace sentence-transformers
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def build_vector_store(chunks, embeddings_model, store_dir="vector_store_db"):
    """
    Builds a FAISS vector database from text chunks and saves it locally.
    
    Args:
        chunks: List of split Document chunks
        embeddings_model: Embedding model to vectorize chunks
        store_dir: Path to directory for local persistence
        
    Returns:
        An instance of FAISS vector store.
    """
    if not chunks:
        return None
        
    # Clear directory to prevent merging old databases
    if os.path.exists(store_dir):
        import time
        for i in range(3):
            try:
                shutil.rmtree(store_dir)
                break
            except Exception:
                time.sleep(0.5)
        
        if os.path.exists(store_dir):
            try:
                for root, dirs, files in os.walk(store_dir, topdown=False):
                    for file in files:
                        try:
                            os.chmod(os.path.join(root, file), 0o777)
                            os.remove(os.path.join(root, file))
                        except Exception:
                            pass
                    for dir in dirs:
                        try:
                            os.rmdir(os.path.join(root, dir))
                        except Exception:
                            pass
                os.rmdir(store_dir)
            except Exception as e:
                print(f"Warning: could not fully clean vector store directory: {e}")
        
    vector_store = FAISS.from_documents(chunks, embeddings_model)
    vector_store.save_local(store_dir)
    return vector_store

def load_vector_store(embeddings_model, store_dir="vector_store_db"):
    """
    Loads an existing FAISS vector database from a local directory.
    
    Args:
        embeddings_model: The embedding model used when saving the index
        store_dir: Path to directory containing saved FAISS index
        
    Returns:
        An instance of FAISS vector store, or None if index doesn't exist.
    """
    if not os.path.exists(store_dir) or not os.path.exists(os.path.join(store_dir, "index.faiss")):
        return None
        
    try:
        # allow_dangerous_deserialization is required for loading local pickle-based FAISS index
        return FAISS.load_local(store_dir, embeddings_model, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"Error loading FAISS vector database: {e}")
        return None

def search_documents(vector_store, query, k=4):
    """
    Queries the vector database for the top-k most relevant chunks matching the user search term.
    
    Args:
        vector_store: FAISS vector database
        query: Search string or question
        k: Number of matching chunks to retrieve
        
    Returns:
        List of matching Document objects.
    """
    if not vector_store:
        return []
    return vector_store.similarity_search(query, k=k)
