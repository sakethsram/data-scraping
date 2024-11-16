import json
from typing import List
from scrapeanddownload import extract_links, clear_and_download_pdf
from PDFtoEMBEDDINGS import gen_emb, background, ask_query

def main():
    # Path to the text file containing links
    txt_file_path = '/home/saketh/coding-python-docs/data-scraping/embeddings/link.txt'
    
    # Extract links from the text file
    links = extract_links(txt_file_path)
    
    # Use the first extracted link to download the PDF
    pdf_url = links[0]
    pdf_path = clear_and_download_pdf(pdf_url)
    
    # Generate embeddings from the downloaded PDF
    embeddings, documents = gen_emb(pdf_path)
    
    # Perform background processing (e.g., storing embeddings in a database)
    result = background()  # Capture the result from background()
    
    # Print the background result (success message)
    print(result)

    # Query the embeddings with a predefined question
    query_text = "what is the proposed project at 2995 atlas road , richmond , california?"
    results = ask_query(query_text)
    
    # Print the query results
    print(results)

if __name__ == "__main__":
    main()
