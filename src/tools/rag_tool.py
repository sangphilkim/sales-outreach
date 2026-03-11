import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

def load_documents(path):
    """
    확장자별 적합한 로더로 문서를 로드합니다.
    - .md, .txt → TextLoader (추가 패키지 불필요)
    - .pdf      → PyPDFLoader (pypdf)
    - .docx     → Docx2txtLoader (docx2txt)
    """
    docs = []

    md_loader = DirectoryLoader(path, glob="**/*.md", loader_cls=TextLoader)
    docs.extend(md_loader.load())

    txt_loader = DirectoryLoader(path, glob="**/*.txt", loader_cls=TextLoader)
    docs.extend(txt_loader.load())

    pdf_loader = DirectoryLoader(path, glob="**/*.pdf", loader_cls=PyPDFLoader)
    docs.extend(pdf_loader.load())

    docx_loader = DirectoryLoader(path, glob="**/*.docx", loader_cls=Docx2txtLoader)
    docs.extend(docx_loader.load())

    return docs

def get_vector_store():
    """Get or create the vector store."""
    database_path = "database"
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    if os.path.exists(database_path) and os.listdir(database_path):
        # Use the existing vector store
        vectorstore = Chroma(persist_directory=database_path, embedding_function=embeddings)
    else:
        # Load documents and create a new vector store
        docs = load_documents("./data/case_studies")
        vectorstore = Chroma.from_documents(docs, embeddings, persist_directory=database_path)

    return vectorstore

def fetch_similar_case_study(description):
    """Fetch the most similar case study to the given description."""
    vectorstore = get_vector_store()
    vectorstore_retreiver = vectorstore.as_retriever(search_kwargs={"k": 1})
    docs = vectorstore_retreiver.invoke(description)
    return docs[0].page_content