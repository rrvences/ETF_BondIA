import pandas as pd



df = pd.read_csv(f"pipelines/ref_data/etfs_ref_data.csv")

records_dict = df.to_dict(orient="records")




print(records_dict)