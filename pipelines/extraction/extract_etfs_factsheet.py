import requests
from bs4 import BeautifulSoup
from pdf2image import convert_from_bytes
from pipelines.general.filesystem_utils import FS_PATH

def extract_factsheet_link(url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Send a GET request to the URL with headers
    response = requests.get(url, headers=headers)

    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        return soup
    else: 
        None


def extract_factsheet_content(factsheet_url:str =  ""):
    factsheet_information = requests.get(factsheet_url)
    return factsheet_information.content


def pdf_bytes_to_single_pdf(pdf_bytes, output_pdf_path):
    # Convert PDF bytes to images
    images = convert_from_bytes(pdf_bytes)

    # Save all images as a single PDF file
    if images:
        # Convert images to RGB mode if they are not
        rgb_images = [image.convert('RGB') for image in images]
        
        # Save as a single PDF
        rgb_images[0].save(output_pdf_path, save_all=True, append_images=rgb_images[1:])
        print(f"Saved: {output_pdf_path}")
    else:
        print("No images to save.")


def read_pdf_file_to_bytes(pdf_path: str):
    # Read the PDF file into bytes
    with open(pdf_path, 'rb') as file:
        pdf_bytes = file.read()
    return pdf_bytes


def extract_and_save_pdf(isin:str = ""):
    just_etf_url = f"https://www.justetf.com/en/etf-profile.html?isin={isin}"
    justetf_soup = extract_factsheet_link(just_etf_url)

    if justetf_soup:

        factsheet_element = justetf_soup.find('a', title='Factsheet (EN)')
        if factsheet_element and 'href' in factsheet_element.attrs:
            factsheet_url = factsheet_element['href']
            factsheet_content = extract_factsheet_content(factsheet_url)
            pdf_bytes_to_single_pdf(factsheet_content,f"{FS_PATH}{isin}_factsheet.pdf")

        else:
            raise Exception("Not able to find En Factsheet")
    
    else:
        raise Exception("Not able to find etf in Just Etf")

    

if __name__ == '__main__':
    extract_and_save_pdf("IE00B6QGFW01")