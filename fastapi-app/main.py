import os
import io
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pipelines.extraction.extract_etfs_factsheet import extract_and_save_pdf, read_pdf_file_to_bytes
from pipelines.extraction.extract_etfs_details import get_etf_daily_prices, get_etf_dividends_issued, get_etf_info
from pipelines.transform.parser_utils import parse_pdf_document, save_json_to_file
from pipelines.general.filesystem_utils import FS_PATH, JSON_PATH, CODE_PATH
from pipelines.mongo.mongo_utils import MongoDBUtils
from fastapi_utils import (
        make_csv_endpoint,
        extract_element_and_insert_into_mongo,
        etf_data_processor,
        log_etfs_info_status
        )

app = FastAPI()


class IsinInput(BaseModel):
    isin: str


@app.get("/element")
def get_element_data(isin: str, element:str):
    # Fetch the maturity record using the helper function
    mongodb = MongoDBUtils()
    record = mongodb.retrieve_record(element,{"isin":isin})
    print(mongodb.retrieve_record("etf_daily_prices",{"isin":"IE00BZ163G84"}))
    mongodb.close_connection()
    print(record)

    return record if record else {"error": "No record found"}


@app.get("/collection_data")
def get_collection_data(collection_name:str):
    # Fetch the maturity record using the helper function
    mongodb = MongoDBUtils()
    records = mongodb.retrieve_all_records(collection_name)
    mongodb.close_connection()

    return records

@app.post("/process_fs_data")
def process_fs_data(data: IsinInput):
    isin = data.isin

    pdf_path = f"{FS_PATH}{isin}_factsheet.pdf"
    json_save_path = f"{JSON_PATH}{isin}_factsheet.json"

    try:
        # Check if the PDF already exists, if not, extract and save it
        if not os.path.exists(pdf_path):
            extract_and_save_pdf(isin)

        # Check if the JSON already exists, if not, parse the PDF and save the JSON
        if not os.path.exists(json_save_path) and os.path.exists(pdf_path):
            json_data = parse_pdf_document(isin)
            save_json_to_file(json_data, isin)

        elif not os.path.exists(json_save_path):
            log_etfs_info_status(isin, "process_fs_data", "No data found")
            raise HTTPException(404, "FactSheet EN or DE not found")

        # Extract and insert data elements into MongoDB
        for element in ["maturity", "sector", "credit_rate", "market_allocation", "portfolio"]:
            extract_element_and_insert_into_mongo(isin, element, json_save_path)

        log_etfs_info_status(isin, "process_fs_data")
        return "ETF Factsheet Processed"

    except Exception as e:
        raise HTTPException(500, f"Error processing data: {str(e)}")

# Define file paths
country_list_ratings_path = os.path.join(CODE_PATH, "pipelines/ref_data/Country_List_Credit_Ratings.csv")
credit_ratings_guide_path = os.path.join(CODE_PATH, "pipelines/ref_data/Credit_Ratings_guide.csv")
interest_rates_path = os.path.join(CODE_PATH, "pipelines/ref_data/Interest_Rates.csv")
country_debt_to_gdp_path = os.path.join(CODE_PATH, "pipelines/ref_data/Country_List_Government_Debt_to_GDP.csv")
etfs_ref_data_path = os.path.join(CODE_PATH, "pipelines/ref_data/etfs_ref_data.csv")

# Register endpoints using functools.partial or the factory
app.get("/country_list_ratings")(make_csv_endpoint(country_list_ratings_path))
app.get("/credit_ratings_guide")(make_csv_endpoint(credit_ratings_guide_path))
app.get("/interest_rates")(make_csv_endpoint(interest_rates_path))
app.get("/country_debt_to_gdp")(make_csv_endpoint(country_debt_to_gdp_path))
app.get("/etfs_list")(make_csv_endpoint(etfs_ref_data_path))


@app.post("/extract_prices")
def extract_daily_prices(isin: str) -> str:
    """Endpoint wrapper for daily prices extraction"""
    return etf_data_processor(
        data_fetcher=get_etf_daily_prices,
        collection_name="etf_daily_prices",
        unique_keys=["isin", "date"]
    )(isin)

@app.post("/extract_dividends")
def extract_dividends_issued(isin: str) -> str:
    """Endpoint wrapper for dividends extraction"""
    return etf_data_processor(
        data_fetcher=get_etf_dividends_issued,
        collection_name="etf_dividends_issued",
        unique_keys=["isin", "date"]
    )(isin)

@app.post("/extract_info")
def extract_info(isin: str) -> str:
    """Endpoint wrapper for general info extraction"""
    return etf_data_processor(
        data_fetcher=get_etf_info,
        collection_name="etf_info",
        unique_keys=["isin"]
    )(isin)

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