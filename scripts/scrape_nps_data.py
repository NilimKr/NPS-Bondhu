
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
import time
import random
import re

# Base URL for relative links
BASE_URL_NPS = "https://npstrust.org.in"

# Configuration
URLS_TO_SCRAPE = {
    "circulars": [
        "https://npstrust.org.in/circulars",
        "https://npstrust.org.in/faqs", # FAQs are also largely PDFs
    ],
    "acts_regulations": [
        "https://npstrust.org.in/act-and-regulations",
    ],
    "faqs": [
        "https://npstrust.org.in/faqs",
    ],
    "direct_pdfs": [
        "https://npstrust.org.in/sites/default/files/act-and-regulations-documents/GazettePFRDAOperationalisationofUPSNPSAmendmentRegulations2025.pdf?",
    ]
}

DOWNLOAD_DIR_PDFS = "data/scraped_pdfs"
DOWNLOAD_DIR_TEXT = "data/scraped_text"

def setup_dirs():
    for d in [DOWNLOAD_DIR_PDFS, DOWNLOAD_DIR_TEXT]:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"Created directory: {d}")

def get_filename_from_url(url):
    parsed_url = urlparse(url)
    path = unquote(parsed_url.path)
    filename = os.path.basename(path)
    if not filename:
        filename = f"document_{int(time.time())}.pdf"
    # Sanitize filename
    filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_', '-')]).rstrip()
    return filename

def download_pdf(url, folder=DOWNLOAD_DIR_PDFS):
    try:
        filename = get_filename_from_url(url)
        filepath = os.path.join(folder, filename)

        if os.path.exists(filepath):
            print(f"File already exists: {filename}")
            return False

        print(f"Downloading PDF: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Saved PDF to: {filepath}")
        return True

    except Exception as e:
        print(f"Failed to download PDF {url}: {e}")
        return False

def scrape_pdf_links(url):
    print(f"\nScraping PDF links from: {url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "lxml")
        
        # Find all links ending in .pdf
        pdf_links = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(BASE_URL_NPS, href)
            
            # Check if it looks like a PDF link
            if full_url.lower().endswith(".pdf") or ".pdf?" in full_url.lower():
                 pdf_links.add(full_url)
        
        print(f"Found {len(pdf_links)} unique PDF links.")
        
        download_count = 0
        for link in pdf_links:
            if download_pdf(link):
                download_count += 1
                time.sleep(random.uniform(1, 3))
            
        print(f"Downloaded {download_count} files from {url}")

    except Exception as e:
        print(f"Error scraping {url}: {e}")

def scrape_faqs(url):
    print(f"\nScraping FAQs from: {url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "lxml")
        
        # Attempt to extract text content intelligently
        # Assuming FAQs are in some container, possibly 'accordion' or 'faq-list'
        # But scraping all paragraphs is a decent fallback
        
        text_content = []
        
        # Specific selectors based on common structures (or just generic text extraction)
        # Trying to find the main content area if possible
        main_content = soup.find("main") or soup.find("div", class_="content") or soup.body
        
        if main_content:
             # Extract structured text
             for elem in main_content.find_all(['h1', 'h2', 'h3', 'p', 'li']):
                 text = elem.get_text(strip=True)
                 if text:
                     text_content.append(text)
        
        full_text = "\n\n".join(text_content)
        
        filename = "nps_faqs.txt"
        filepath = os.path.join(DOWNLOAD_DIR_TEXT, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Source: {url}\n\n")
            f.write(full_text)
            
        print(f"Saved FAQ text to: {filepath}")

    except Exception as e:
        print(f"Error scraping FAQs from {url}: {e}")

def main():
    print("--- NPS Trust Data Scraper ---")
    setup_dirs()
    
    # 1. Scrape Circulars (PDFs)
    for url in URLS_TO_SCRAPE["circulars"]:
        scrape_pdf_links(url)
        time.sleep(2)

    # 2. Scrape Acts & Regulations (PDFs)
    for url in URLS_TO_SCRAPE["acts_regulations"]:
        scrape_pdf_links(url)
        time.sleep(2)

    # 3. Download Direct PDFs
    for url in URLS_TO_SCRAPE["direct_pdfs"]:
        download_pdf(url)
        time.sleep(1)

    # 4. Scrape FAQs (Text)
    for url in URLS_TO_SCRAPE["faqs"]:
        scrape_faqs(url)
        time.sleep(1)
        
    print("\nScraping complete.")

if __name__ == "__main__":
    main()
