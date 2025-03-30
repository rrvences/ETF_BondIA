
import json
import os
from llama_cloud_services import LlamaParse

# set up parser
llama_parser = LlamaParse(
    result_type="json",
    api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
    extract_charts = True,
    premium_mode= True
)


def parse_pdf_document(isin:str):
    file_path = f"/app/data/factsheet/{isin}_factsheet.pdf"
    json_objs = llama_parser.get_json_result(file_path)
    jsons_save_path = f"/app/data/json/{isin}_factsheet.json"
    
    with open(jsons_save_path, "w", encoding="utf-8") as json_file:
        json.dump(json_objs[0]['pages'], json_file)

    print(f"Json file for {isin} saved as {jsons_save_path}")


    

   