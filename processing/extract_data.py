import os
import pandas as pd

# Function to extract table data from markdown content
def extract_table(markdown_lines, start_index):
    table_data = []
    headers = []
    for i in range(start_index, len(markdown_lines)):
        line = markdown_lines[i].strip()
        
        # Stop if we reach an empty line or a new heading
        if line == "" or line.startswith("#"):
            break
        
        # Skip separator row (e.g., |---|---|---|...)
        if "---" in line:
            continue
        
        # Extract table rows
        row = [cell.strip() for cell in line.split("|") if cell.strip()]
        
        if not headers:
            headers = row  # First row is the header
        else:
            table_data.append(row)  # Append actual data

    return headers, table_data

# Function to extract both performance tables from markdown content
def extract_data_from_markdown(markdown_content):
    lines = markdown_content.split("\n")
    
    # Extract Calendar Year Performance
    try:
        cal_year_index = next(i for i, line in enumerate(lines) if "CALENDAR YEAR PERFORMANCE" in line)
        cy_headers, cy_data = extract_table(lines, cal_year_index + 2)
    except StopIteration:
        cy_headers, cy_data = [], []
    
    # Extract Cumulative & Annualized Performance
    try:
        cum_perf_index = next(i for i, line in enumerate(lines) if "CUMULATIVE & ANNUALISED PERFORMANCE" in line)
        cum_headers, cum_data = extract_table(lines, cum_perf_index + 3)
    except StopIteration:
        cum_headers, cum_data = [], []

    # Convert to DataFrame
    df_calendar_year = pd.DataFrame(cy_data, columns=cy_headers[1:]) if cy_headers else pd.DataFrame()
    df_cumulative = pd.DataFrame(cum_data, columns=cum_headers[1:]) if cum_headers else pd.DataFrame()

    if not df_calendar_year.empty:
        df_calendar_year.insert(0, "Year", ["Share Class", "Benchmark"])
    
    if not df_cumulative.empty:
        df_cumulative.insert(0, "Period", ["Share Class", "Benchmark"])

    return df_calendar_year, df_cumulative


if __name__ == '__main__':

    file_path = os.path.join(os.getcwd(), 'files', 'markdown')
    files = os.listdir(file_path)

    for file in files:

        with open(os.path.join(file_path, file), "r", encoding="utf-8") as md_file:
            markdown_content = md_file.read()

        
