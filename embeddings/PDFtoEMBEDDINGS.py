import json
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
import chromadb

# Define global variables for collection and client to ensure persistence
vdb_name = "aura-vectorDB"
cname = "pdf-embeddings-coll"

def gen_emb(pdf_path):
    """Generate embeddings from a PDF file."""
    # Load the PDF file
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    
    # Split the document into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(pages)

    # Initialize the VertexAI model for embeddings
    embeddings_model = VertexAIEmbeddings(model_name="textembedding-gecko@latest")
    text_chunks = [chunk.page_content for chunk in chunks]
    
    # Generate embeddings for the text chunks
    embeddings = embeddings_model.embed_documents(text_chunks)
    return embeddings, text_chunks

def background():
    """Generate and store embeddings."""
    # Generate embeddings
    pdf_path = "/home/saketh/coding-python-docs/data-scraping/sample-pdfs/downlad-pdf-using-python/f1.pdf"
    embeddings, documents = gen_emb(pdf_path)

    client = chromadb.PersistentClient(path=vdb_name)
    collection = client.get_or_create_collection(name=cname)

    # Store embeddings in the collection
    collection.upsert(
        documents=documents,
        metadatas=[{"source": "pdf"} for _ in documents],
        ids=[str(i) for i in range(len(documents))]
    )
    print("Embeddings stored in collection.")

    # Return a success message
    return "Embeddings successfully stored in the database."

def ask_query(query_text: str):
    """Query the stored embeddings collection for relevant answers."""
    client = chromadb.PersistentClient(path=vdb_name)
    collection = client.get_or_create_collection(name=cname)

    # Query the collection with the input text
    results = collection.query(
        query_texts=[query_text],
        n_results=2,
        where={"source": "pdf"}
    )
    
    # Print and return the results
    return results
