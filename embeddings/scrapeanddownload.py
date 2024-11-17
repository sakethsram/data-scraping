import re
import os
import requests

def extract_links(file_path):
    links = []
    with open(file_path, 'r') as file:
        content = file.read()        
    links = re.findall(r'(https?://[^\s]+)', content)  
    print("link is extracted")  
    return links

def clear_and_download_pdf(url:str):
    folder_path = "/home/saketh/coding-python-docs/data-scraping/sample-pdfs/download-using-python"
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder {folder_path} created.")
    
    # Clear existing PDFs in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    
    # Download the new PDF
    response = requests.get(url)
    if response.status_code == 200:
        pdf_path = os.path.join(folder_path, "f1.pdf")
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(response.content)
        print("PDF downloaded and saved.")
        return pdf_path
    
    
def main():
    # Path to the text file containing the link
    links_file_path = "/home/saketh/coding-python-docs/data-scraping/links-from-text.txt"
    
    # Extract links from the text file
    links = extract_links(links_file_path)
    
    # Download the PDF from the first link
    pdf_url = links[0]  # Assuming the first link is the one to download
    pdf_path = clear_and_download_pdf(pdf_url)
    print(f"PDF downloaded and saved at: {pdf_path}")

if __name__ == "__main__":
    main()