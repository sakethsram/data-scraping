import json
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
import chromadb
import re
import os
import requests
from scrapeanddownload import extract_links, clear_and_download_pdf
from PDFtoEMBEDDINGS import gen_emb, background, ask_query,rate_limit,total
from embed-copy import load_and_split_document,generate_embeddings,answer_query
def main():
    txt_file_path = '/home/saketh/coding-python-docs/data-scraping/links-from-text.txt'

    links = extract_links(txt_file_path)    
    pdf_url = links[0]
    pdf_path = clear_and_download_pdf(pdf_url)
    
    q = "What is the project title for the Atlas Road Industrial Building Project?"

if __name__ == "__main__":
    main()
