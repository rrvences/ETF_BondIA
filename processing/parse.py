
import json
import os
# bring in our LLAMA_CLOUD_API_KEY

from dotenv import load_dotenv
load_dotenv()

# bring in deps
from llama_cloud_services import LlamaParse
from llama_index.core import SimpleDirectoryReader

# set up parser
parser = LlamaParse(
    result_type="json"  # "markdown" and "text" are available
)

files_to_process = [os.path.join(os.getcwd(), 'files', 'factsheets', file) for file in os.listdir('files/factsheets') if f'output_{file.split('.')[0]}.json' not in os.listdir('files/json')]

#file = "MR_FR_en_IE00BZ163G84_RES_2025-02-28.pdf"

#file_path = os.path.join(os.getcwd(), 'files', 'factsheets', file)


# # use SimpleDirectoryReader to parse our file
# file_extractor = {".pdf": parser}


# documents_jsons = SimpleDirectoryReader(input_files=files_to_process, 
#                                   file_extractor=file_extractor).load_data()

# Specify the file name

# Save the Json content to a file
for di, file_path in enumerate(files_to_process):

    json_objs = parser.get_json_result(file_path)

    file_save_path = os.path.join(os.getcwd(), 'files', 'json', f'output_{file_path.split(os.sep)[-1].split('.')[0]}.json')
    
    with open(file_save_path, "w", encoding="utf-8") as json_file:
        json.dump(json_objs[0]['pages'], json_file)

    print(f"Json file {di} saved as {file_save_path}")