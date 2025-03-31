
import json
import os
from llama_cloud_services import LlamaParse
from pipelines.general.filesystem_utils import FS_PATH, JSON_PATH 

# set up parser
llama_parser = LlamaParse(
    result_type="json",
    api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
    extract_charts = True,
    auto_mode = True,
    auto_mode_trigger_on_table_in_page = True,
    auto_mode_trigger_on_image_in_page = True
)


def parse_pdf_document(isin: str):
    """
    Parses a PDF document and returns the JSON objects extracted from it.
    
    Args:
        isin (str): The ISIN code used to locate the PDF file.
    
    Returns:
        list: A list of JSON objects extracted from the PDF.
    """
    file_path = f"{FS_PATH}{isin}_factsheet.pdf"
    json_objs = llama_parser.get_json_result(file_path)
    return json_objs[0]['pages']  # Return the pages from the JSON objects


def save_json_to_file(json_data, isin: str):
    """
    Saves the given JSON data to a file.
    
    Args:
        json_data (list): The JSON data to save.
        isin (str): The ISIN code used to name the JSON file.
    """
    jsons_save_path = f"{JSON_PATH}{isin}_factsheet.json"
    
    with open(jsons_save_path, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file)

    print(f"Json file for {isin} saved as {jsons_save_path}")