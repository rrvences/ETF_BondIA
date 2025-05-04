import logging
import os
import pandas as pd
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from functools import partial
from fastapi.responses import JSONResponse
from pipelines.mongo.mongo_utils import MongoDBUtils
from typing import Dict, Any, Callable, List, Optional
from pymongo.results import UpdateResult
from pipelines.general.filesystem_utils import CODE_PATH
from pipelines.transform.process_json_data import (
    extract_maturity,
    extract_market_allocation,
    extract_credit_rate,
    extract_sector,
    extract_portfolio_characteristics,
)

app = FastAPI()



def load_csv_as_records(file_path: str):
    """
    Utility function to load a CSV file, fill NA values, and return a list of records.
    Handles file not found and parsing errors.
    """
    try:
        df = pd.read_csv(file_path)
        df.fillna(value="NA", inplace=True)
        return df.to_dict(orient="records")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except pd.errors.ParserError:
        raise HTTPException(
            status_code=400, detail=f"Error parsing CSV file: {file_path}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


def make_csv_endpoint(file_path: str):
    """
    Returns a FastAPI endpoint function that loads a CSV and returns its records.
    """

    def endpoint():
        records = load_csv_as_records(file_path)
        return JSONResponse(content=records)

    return endpoint


def extract_element_and_insert_into_mongo(
    isin: str, element: str, json_save_path: str
) -> UpdateResult:
    """
    Extracts a specified element from a JSON file and upserts it into MongoDB.

    Args:
        isin (str): The ISIN code for the record.
        element (str): Element type to extract (e.g., "maturity", "sector").
        json_save_path (str): Path to the JSON file containing the data.

    Returns:
        UpdateResult: MongoDB upsert result.

    Raises:
        ValueError: For invalid element types or extraction errors.
        RuntimeError: For MongoDB operation failures.
    """
    function_dict: Dict[str, Callable[[str], Any]] = {
        "maturity": extract_maturity,
        "sector": extract_sector,
        "credit_rate": extract_credit_rate,
        "market_allocation": extract_market_allocation,
        "portfolio": extract_portfolio_characteristics,
    }

    # Validate element early
    if element not in function_dict:
        raise ValueError(
            f"Invalid element: {element}. Valid options: {list(function_dict.keys())}"
        )

    mongodb = MongoDBUtils()
    result = None

    try:
        # Extract data
        extracted_data = function_dict[element](json_save_path)
        if not extracted_data:
            logging.error(f"No data extracted for {element} from {json_save_path}")

        # Prepare and upsert record
        record_data = {"isin": isin, element: extracted_data or {}}
        result = mongodb.upsert_record(
            collection_name=element,
            record=record_data,
            unique_keys=["isin"],  # Upsert based on ISIN
        )

        logging.info(f"Upserted {element} for ISIN {isin}: {result.raw_result}")
        return result

    except Exception as e:
        logging.error(f"Failed to process {element} for ISIN {isin}: {str(e)}")
        raise RuntimeError(f"Operation failed: {str(e)}") from e

    finally:
        mongodb.close_connection()


def log_etfs_info_status(isin: str, element: str, status: str = "Succeeded"):
    mongodb = MongoDBUtils()

    info_status = {
        "isin": isin,
        "element": element,
        "status": status,
        "date": datetime.now(timezone.utc),
    }

    mongodb.upsert_record("etf_info_status", info_status, ["isin", "element"])
    mongodb.close_connection()


def lookup_etf_ref_data(search_value: str, search_col: str, return_col: str, case_insensitive: bool = False) -> Optional[str]:
    """
    Internal helper to look up values in the ETF reference data CSV.

    Args:
        search_value (str): The value to search for.
        search_col (str): The column to search in.
        return_col (str): The column to return from the matching row.
        case_insensitive (bool): Whether to perform a case-insensitive search.

    Returns:
        Optional[str]: The found value, or None if not found.
    """
    csv_path = os.path.join(CODE_PATH, "pipelines/ref_data/etfs_ref_data.csv")
    df = pd.read_csv(csv_path)
    # Perform case-insensitive search if requested
    if case_insensitive:
        mask = df[search_col].str.upper() == search_value.upper()
    else:
        mask = df[search_col] == search_value
    result = df[mask]
    if not result.empty:
        return result[return_col].values[0]
    return None

# Create partial functions for each lookup scenario
get_isin_from_ticker = partial(lookup_etf_ref_data, search_col="ticker", return_col="isin", case_insensitive=True)
get_ticker_from_isin = partial(lookup_etf_ref_data, search_col="isin", return_col="ticker", case_insensitive=False)


def etf_data_processor(
    data_fetcher: Callable[[str], pd.DataFrame],
    collection_name: str,
    unique_keys: List[str]
):
    def process_data(isin: str):
        try:
            # Common pre-processing
            ticker = get_ticker_from_isin(isin)
            if not ticker:
                log_etfs_info_status(isin, collection_name, "No ticker found")
                raise HTTPException(404, f"No ticker found for ISIN: {isin}")

            # Data fetching
            df = data_fetcher(ticker)
            result_dict = df.groupby('ticker').apply(lambda x: x.to_dict(orient='records')).to_dict()
            mongodb = MongoDBUtils()

            # Assuming result_dict is your dictionary with tickers as keys
            for ticker, records in result_dict.items():
                # Insert each record into the collection
                for record_data in records:
                    record_data["isin"] = isin
                    mongodb.upsert_record(collection_name, record_data, unique_keys)


            log_etfs_info_status(isin, collection_name)
            return f"Processed {len(records)} records for {collection_name}"

        except HTTPException:
            raise
        except Exception as e:
            log_etfs_info_status(isin, collection_name, str(e))
            raise HTTPException(500, f"Processing failed: {str(e)}")

    return process_data