import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_vertexai import VertexAI, VertexAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA 
import time
from langchain.chains import LLMChain
import time

def load_and_split_document(pdf_file):
    loader = PyPDFLoader(pdf_file)
    pages = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(pages)
    return chunks

def generate_embeddings(chunks, requests_per_minute=100, num_instances_per_batch=5):
    used_llm = VertexAI(
        model_name="gemini-1.5-pro",
        max_output_tokens=2048,
        temperature=0.1,
        verbose=False,
    )

    class CustomVertexAIEmbeddings(VertexAIEmbeddings):
        requests_per_minute: int
        num_instances_per_batch: int
        model_name: str

        def embed_documents(self, texts):
            limiter = rate_limit(self.requests_per_minute)

            results = []
            docs = list(texts)

            while docs:
                head, docs = (
                    docs[: self.num_instances_per_batch],
                    docs[self.num_instances_per_batch:],
                )
                chunk = self.client.get_embeddings(head)
                results.extend(chunk)
                next(limiter)

            return [r.values for r in results]

    embeddings = CustomVertexAIEmbeddings(
        requests_per_minute=requests_per_minute,
        num_instances_per_batch=num_instances_per_batch,
        model_name="textembedding-gecko@latest",
    )

    text_chunks = [chunk.page_content for chunk in chunks]

    db = FAISS.from_texts(text_chunks, embeddings)

    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )

    return retriever, used_llm

def answer_query(query, retriever, used_llm):
    prompt_RAG = (
        "You are a RAG model designed to answer queries using the content from the provided document. "
        "If the document contains the answer, provide a precise response based on it. "
        "If the answer isn't in the document, respond with: 'Context not found.'"
    )

    prompt_RAG_template = PromptTemplate(
        template=prompt_RAG,
        input_variables=["context", "question"], 
    )

    llm_chain = LLMChain(
        llm=used_llm,
        prompt=prompt_RAG_template,
    )

    qa_chain = RetrievalQA.from_llm(
        llm=used_llm,
        retriever=retriever,
        return_source_documents=True,
    )

    results = qa_chain.invoke(input={"query": query})
    return results["result"]

def rate_limit(max_per_minute):
    period = 60 / max_per_minute
    while True:
        before = time.time() 
        yield  
        after = time.time() 
        elapsed = after - before
        sleep_time = max(0, period - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)

def total(pdf_files, q):   
    retrievers = []
    for pdf_file in pdf_files:
        print(f"Generating embeddings for {os.path.basename(pdf_file)}...")
        chunks = load_and_split_document(pdf_file)   
        retriever, used_llm = generate_embeddings(chunks)
        retrievers.append(retriever)


    answers = []
    for retriever in retrievers:
        answer = answer_query(q, retriever, used_llm)
        answers.append(answer)

    print("Final Answer:", answers[-1])

folder_path = "/home/saketh/coding-python-docs/data-scraping/sample-pdfs"
pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.pdf') and not f.endswith(':Zone.Identifier')]

q = "tell me about the project in springfields"

total(pdf_files, q)
