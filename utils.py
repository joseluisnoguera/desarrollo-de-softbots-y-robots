import os
import streamlit as st
import uuid
from streamlit.logger import get_logger
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.tools import DuckDuckGoSearchRun

logger = get_logger('Langchain-Chatbot')

# Constants
GEMINI_MODEL_NAME = "gemini-1.5-flash"
PRIVATE_DATA_DIR = "data" # Private data directory

#decorator
def enable_chat_history(func):
    if os.environ.get("GOOGLE_API_KEY"):

        # to clear chat history after switching chatbot
        current_page = func.__qualname__
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = current_page
        if st.session_state["current_page"] != current_page:
            try:
                st.cache_resource.clear()
                del st.session_state["current_page"]
                del st.session_state["messages"]
                del st.session_state["session_id"]
            except Exception as e:
                st.warning(f"Failed to clear session state: {e}")

        # Only initialize messages, do not display them here
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "¿Cómo puedo ayudarte hoy?"}]

        # Generate and store a unique session_id if not present
        if "session_id" not in st.session_state:
            st.session_state["session_id"] = str(uuid.uuid4())

    def execute(*args, **kwargs):
        func(*args, **kwargs)
    return execute

def display_msg(msg, author):
    """Display a message in the chat UI."""
    st.chat_message(author).write(msg)

def configure_llm():
    # They come by default with the model
    # safety_settings = [
    #     {"category": "HARM_CATEGORY_DEROGATORY", "threshold": 1},
    #     {"category": "HARM_CATEGORY_VIOLENCE", "threshold": 2},
    #     {"category": "HARM_CATEGORY_SEXUAL", "threshold": 2},]
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME,
        temperature=0,
        disable_streaming=False,
        api_key=st.secrets["GOOGLE_API_KEY"]
    )
    return llm

def print_qa(cls, question, answer):
    log_str = "\nUsecase: {}\nQuestion: {}\nAnswer: {}\n" + "------"*10
    logger.info(log_str.format(cls.__name__, question, answer))

@st.cache_resource
def configure_embedding_model():
    embedding_model = FastEmbedEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") # Ejemplo multilingüe
    return embedding_model

# --- RAG Tool ---
@st.cache_resource(show_spinner="Cargando y procesando datos privados...")
def setup_vector_store(data_dir=PRIVATE_DATA_DIR):
    # TextLoader loads text files, use other loaders for different formats
    loader = DirectoryLoader(data_dir, glob="**/*.txt", loader_cls=TextLoader, show_progress=True)
    docs = loader.load()

    if not docs:
        logger.warning(f"No se encontraron documentos en {data_dir}. El RAG no funcionará.")
        return None

    # Text Splitter into chunks, play with chunk_size and chunk_overlap
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    splits = text_splitter.split_documents(docs)

    embedding_model = configure_embedding_model()

    # FAISS is a vector store library that allows for efficient similarity search locally
    try:
        vectorstore = FAISS.from_documents(documents=splits, embedding=embedding_model)
        logger.info(f"Vector store creado con {len(splits)} chunks.")
        return vectorstore
    except Exception as e:
        logger.error(f"Error al crear el vector store FAISS: {e}")
        st.error(f"Error al procesar los datos privados: {e}")
        return None

def get_retriever():
    vectorstore = setup_vector_store()
    if vectorstore:
        # search_kwargs={'k': 3} means return 3 most relevant chunks
        return vectorstore.as_retriever(search_kwargs={'k': 3})
    return None

# --- Web Search Tool ---
def get_web_search_tool():
    """Crea y retorna la herramienta de búsqueda web DuckDuckGo."""
    search = DuckDuckGoSearchRun()
    return search

def sync_st_session():
    for k, v in st.session_state.items():
        st.session_state[k] = v