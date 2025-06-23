import os
import streamlit as st
import uuid
from streamlit.logger import get_logger
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_qdrant import QdrantVectorStore  # <--- Cambiado aquí
from qdrant_client import QdrantClient
from langchain_core.tools import BaseTool
import requests
import json
import time

logger = get_logger('Langchain-Chatbot')
logger.setLevel("DEBUG")

# Constants
GEMINI_MODEL_NAME = "gemini-1.5-flash"
PRIVATE_DATA_DIR = "data" # Private data directory
QDRANT_HOST = os.environ.get("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.environ.get("QDRANT_PORT", 6333))
QDRANT_COLLECTION = "rag_documents"
QDRANT_USER_COLLECTION = "user_info"

USER_DATA_DIR = os.path.join(os.path.dirname(__file__), "user_data")
os.makedirs(USER_DATA_DIR, exist_ok=True)

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
    try:
        vectorstore = QdrantVectorStore.from_documents(
            documents=splits,
            embedding=embedding_model,  # <--- corregido aquí para langchain-qdrant
            url=f"http://{QDRANT_HOST}:{QDRANT_PORT}",
            collection_name=QDRANT_COLLECTION
        )
        logger.info(f"Vector store Qdrant creado con {len(splits)} chunks.")
        return vectorstore
    except Exception as e:
        logger.error(f"Error al crear el vector store Qdrant: {e}")
        st.error(f"Error al procesar los datos privados: {e}")
        return None

def store_user_info_vector(user_uuid, user_info, embedding_model=None):
    if embedding_model is None:
        embedding_model = configure_embedding_model()
    qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # --- Crear colección si no existe ---
    from qdrant_client.http import models as qdrant_models
    collections = qdrant_client.get_collections().collections
    if QDRANT_USER_COLLECTION not in [c.name for c in collections]:
        qdrant_client.create_collection(
            collection_name=QDRANT_USER_COLLECTION,
            vectors_config=qdrant_models.VectorParams(
                size=embedding_model.embedding_size if hasattr(embedding_model, 'embedding_size') else 384,
                distance=qdrant_models.Distance.COSINE
            )
        )
    # --- Fin crear colección ---
    vectorstore = QdrantVectorStore(
        client=qdrant_client,
        collection_name=QDRANT_USER_COLLECTION,
        embedding=embedding_model
    )
    unique_id = str(uuid.uuid4())
    vectorstore.add_texts(
        [user_info],
        ids=[unique_id],
        metadatas=[{"user_uuid": user_uuid, "timestamp": int(time.time()*1000)}]
    )
    logger.info(f"User info vector almacenado para {user_uuid} con id {unique_id}")

def get_retriever():
    vectorstore = setup_vector_store()
    if vectorstore:
        # search_kwargs={'k': 3} means return 3 most relevant chunks
        return vectorstore.as_retriever(search_kwargs={'k': 3})
    return None

# --- Web Search Tool ---
def get_web_search_tool():
    """Crea y retorna una herramienta de búsqueda web usando la API de Serper.dev compatible con LangChain."""
    import streamlit as st
    import requests
    from langchain_core.tools import BaseTool

    class SerperSearchTool(BaseTool):
        name: str = "serper_search"
        description: str = (
            "Motor de búsqueda Serper.dev. Útil para responder preguntas sobre eventos actuales, conocimiento general o temas de turismo no cubiertos en los documentos privados. La entrada debe ser una consulta de búsqueda."
        )
        api_key: str

        def _run(self, query: str) -> str:
            url = "https://google.serper.dev/search"
            headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
            data = {"q": query}
            try:
                resp = requests.post(url, headers=headers, json=data, timeout=10)
                resp.raise_for_status()
                results = resp.json().get("organic", [])
                if not results:
                    return "No se encontraron resultados."
                return "\n\n".join(f"{item['title']}: {item['link']}\n{item.get('snippet','')}" for item in results[:3])
            except Exception as e:
                return f"Error en búsqueda Serper: {e}"

        def _arun(self, query: str):
            raise NotImplementedError("Async no implementado para SerperSearchTool")

    api_key = st.secrets["SERPER_API_KEY"]
    return SerperSearchTool(api_key=api_key)

def sync_st_session():
    for k, v in st.session_state.items():
        st.session_state[k] = v

def save_user_info_to_disk(user_uuid, info_list):
    """Guarda la lista de info de usuario en un archivo JSON por usuario."""
    path = os.path.join(USER_DATA_DIR, f"{user_uuid}.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(info_list, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error guardando info usuario en disco: {e}")

def load_user_info_from_disk(user_uuid):
    """Carga la lista de info de usuario desde disco, o [] si no existe."""
    path = os.path.join(USER_DATA_DIR, f"{user_uuid}.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando info usuario de disco: {e}")
    return []