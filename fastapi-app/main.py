import os
import io
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Dict, Callable, Any
from pipelines.extraction.extract_etfs_factsheet import extract_and_save_pdf, read_pdf_file_to_bytes
from pipelines.extraction.extract_etfs_details import get_etf_daily_prices, get_etf_dividends_issued, get_etf_info
from pipelines.transform.parser_utils import parse_pdf_document, save_json_to_file
from pipelines.general.filesystem_utils import FS_PATH, JSON_PATH, CODE_PATH
from pipelines.mongo.mongo_utils import MongoDBUtils
from pipelines.transform.process_json_data import (extract_maturity,
                                                    extract_market_allocation, 
                                                    extract_credit_rate,
                                                    extract_sector,
                                                    extract_portfolio_characteristics
                                                    )
from pipelines.transform.convert_data_uniformization import clean_table



app = FastAPI()


class IsinInput(BaseModel):
    isin: str


def get_isin_from_ticker(ticker: str):
    df = pd.read_csv(f"{CODE_PATH}pipelines/ref_data/etfs_ref_data.csv")
    result = df[df['ticker'].str.upper() == ticker.upper()]
    if not result.empty:
        return result['isin'].values[0]
    else:
        return None


def get_ticker_from_isin(isin: str):
    df = pd.read_csv(f"{CODE_PATH}pipelines/ref_data/etfs_ref_data.csv")
    result = df[df['isin'] == isin]
    if not result.empty:
        return result['ticker'].values[0]
    else:
        return None


@app.get("/element")
def get_element_data(isin: str, element:str):
    # Fetch the maturity record using the helper function
    mongodb = MongoDBUtils()
    record = mongodb.retrieve_record(element,{"isin":isin})
    mongodb.close_connection()
    print(record)

    return record

@app.get("/clean_element")
def get_element_data_clean(isin:str, element:str):
    mongodb = MongoDBUtils()
    record = mongodb.retrieve_record(element,{"isin":isin})
    
    mongodb.close_connection()
    if len(record) == 1:
        record = {element: clean_table(record[0][element], element)}
    else:
        record = None
    print(f'Fetching data: {record} \n ----')
    return record 

@app.post("/process")
def process_data(data: IsinInput):
    # Extract the ISIN from the input
    isin = data.isin

    # Define file paths
    pdf_path = f"{FS_PATH}{isin}_factsheet.pdf"
    json_save_path = f"{JSON_PATH}{isin}_factsheet.json"

    # Check if the PDF already exists
    if not os.path.exists(pdf_path):
        print(extract_and_save_pdf(isin))  # Only execute if PDF does not exist

    # Check if the JSON already exists
    if not os.path.exists(json_save_path) and os.path.exists(pdf_path):
        json_data = parse_pdf_document(isin)  # Only execute if JSON does not exist
        save_json_to_file(json_data, isin)

    if not os.path.exists(json_save_path):
        return "Not Json Found"

    for element in ["maturity","sector","credit_rate","market_allocation", "portfolio"]:
        
        extract_element_and_insert_into_mongo(isin,element,json_save_path)

    return "Isin Processed"

@app.post("/extract_prices")
def extract_daily_prices(isin: str):
    
    ticker = get_ticker_from_isin(isin)
    daily_prices_df =  get_etf_daily_prices(ticker)
    result_dict = daily_prices_df.groupby('ticker').apply(lambda x: x.to_dict(orient='records')).to_dict()

    mongodb = MongoDBUtils()


    # Assuming result_dict is your dictionary with tickers as keys
    for ticker, records in result_dict.items():
        # Insert each record into the collection
        for record_data in records:
            record_data["isin"] = isin
            mongodb.upsert_record("etf_daily_prices", record_data, ["isin","date"])

    mongodb.close_connection()

    return "Daily Prices Processed"

@app.post("/extract_dividends")
def extract_dividends_issued(isin: str):

    ticker = get_ticker_from_isin(isin)
    daily_prices_df =  get_etf_dividends_issued(ticker)
    result_dict = daily_prices_df.groupby('ticker').apply(lambda x: x.to_dict(orient='records')).to_dict()
    mongodb = MongoDBUtils()

    # Assuming result_dict is your dictionary with tickers as keys
    for ticker, records in result_dict.items():
        # Insert each record into the collection
        for record_data in records:
            record_data["isin"] = isin
            mongodb.upsert_record("etf_dividends_issued", record_data, ["isin","date"])

    mongodb.close_connection()

    return "Dividends Processed"

@app.post("/extract_info")
def extract_info(isin: str):

    ticker = get_ticker_from_isin(isin)
    daily_prices_df =  get_etf_info(ticker)
    result_dict = daily_prices_df.groupby('ticker').apply(lambda x: x.to_dict(orient='records')).to_dict()
    mongodb = MongoDBUtils()

    # Assuming result_dict is your dictionary with tickers as keys
    for ticker, records in result_dict.items():
        # Insert each record into the collection
        for record_data in records:
            record_data["isin"] = isin
            mongodb.upsert_record("etf_info", record_data, "isin")

    mongodb.close_connection()

    return "Etf Info Processed"

def extract_element_and_insert_into_mongo(isin: str, element: str, json_save_path: str):
    """
    Extracts a specified element from a JSON file and inserts it into MongoDB if it doesn't already exist.

    Args:
        isin (str): The ISIN code for the record.
        element (str): The type of element to extract (e.g., "maturity", "sector", "credit_rate", "market_allocation").
        json_save_path (str): The path to the JSON file from which to extract the data.
    """
    # Mapping of element types to extraction functions
    function_dict: Dict[str, Callable[[str], Any]] = {
        "maturity": extract_maturity,
        "sector": extract_sector,
        "credit_rate": extract_credit_rate,
        "market_allocation": extract_market_allocation,
        "portfolio": extract_portfolio_characteristics
    }
    
    # Check if the provided element is valid
    if element not in function_dict:
        raise ValueError(f"Invalid element type: {element}. Must be one of {list(function_dict.keys())}.")
    
    mongodb = MongoDBUtils()

    # If the record does not exist, extract the data
    extracted_data = function_dict[element](json_save_path)

    # Prepare the record for insertion
    record_data = {"isin": isin, element: extracted_data}

    # Insert the new record into MongoDB
    insert_result = mongodb.upsert_record(element, record_data,"isin")
    print(insert_result)  # Optionally print the result of the insertion


@app.get("/country_list_ratings")
def get_country_list_ratings():
    # Read the CSV file into a DataFrame
    df = pd.read_csv(f"{CODE_PATH}pipelines/ref_data/Country_List_Credit_Ratings.csv")
    df.fillna(value="NA", inplace=True)
    # Convert the DataFrame to a dictionary
    records_dict = df.to_dict(orient="records")  # Convert to list of dictionaries
    return JSONResponse(content=records_dict)


@app.get("/credit_ratings_guide")
def get_country_ratings_guide():
    # Read the CSV file into a DataFrame
    df = pd.read_csv(f"{CODE_PATH}pipelines/ref_data/Credit_Ratings_guide.csv")
    df.fillna(value="NA", inplace=True)
    # Convert the DataFrame to a dictionary
    records_dict = df.to_dict(orient="records")  # Convert to list of dictionaries
    return JSONResponse(content=records_dict)

@app.get("/interest_rates")
def get_interest_rates():
    # Read the CSV file into a DataFrame
    df = pd.read_csv(f"{CODE_PATH}pipelines/ref_data/Interest_Rates.csv")
    df.fillna(value="NA", inplace=True)
    # Convert the DataFrame to a dictionary
    records_dict = df.to_dict(orient="records")  # Convert to list of dictionaries
    return JSONResponse(content=records_dict)

@app.get("/country_debt_to_gdp")
def get_country_debt_to_gdp():
    # Read the CSV file into a DataFrame
    df = pd.read_csv(f"{CODE_PATH}pipelines/ref_data/Country_List_Government_Debt_to_GDP.csv")
    df.fillna(value="NA", inplace=True)
    # Convert the DataFrame to a dictionary
    records_dict = df.to_dict(orient="records")  # Convert to list of dictionaries
    return JSONResponse(content=records_dict)

@app.get("/records")
def get_records():
    # Read the CSV file into a DataFrame
    df = pd.read_csv(f"{CODE_PATH}pipelines/ref_data/etfs_ref_data.csv")
    df.fillna(value="NA", inplace=True)
    # Convert the DataFrame to a dictionary
    records_dict = df.to_dict(orient="records")  # Convert to list of dictionaries
    return JSONResponse(content=records_dict)


@app.get("/read_pdf")
def read_pdf_records(isin: str):
    # Validate the ISIN parameter if necessary
    if not isin or len(isin) != 12:  # Example validation for ISIN length
        raise HTTPException(status_code=422, detail="Invalid ISIN provided.")

    pdf_path = f"{FS_PATH}/{isin}_factsheet.pdf"
    try:
        pdf_content = read_pdf_file_to_bytes(pdf_path)
        return StreamingResponse(io.BytesIO(pdf_content), media_type='application/pdf')
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing the request.")

@app.get("/pdf-records")
def get_pdf_records():
    # Read the CSV file into a DataFrame
    list_of_pdfs = os.listdir(FS_PATH)
    pdf_records = [ pdf.replace("_factsheet.pdf","") for pdf in list_of_pdfs]
    return pdf_records

@app.get("/json-records")
def get_json_records():
    # Read the CSV file into a DataFrame
    list_of_json = os.listdir(JSON_PATH)
    json_records = [ pdf.replace("_factsheet.json","") for pdf in list_of_json]
    return json_records


#print(extract_daily_prices("IE00BZ163G84"))
#print(get_element_data("IE00BZ163G84","etf_daily_prices"))