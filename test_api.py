import pandas as pd
import requests
from src.predict import feature_columns

# Load the dataset
data_file = "data/raw/CIC-IDS2017/Monday-WorkingHours.pcap_ISCX.csv"

df = pd.read_csv(data_file)
df.columns = df.columns.str.strip()

# Select one network flow
sample = df[feature_columns].iloc[[0]]

# Convert to API format
payload = {
    "data": sample.to_dict(orient="records")
}

# Send request to FastAPI
response = requests.post(
    "http://127.0.0.1:8000/predict",
    json=payload
)

print("Status code:", response.status_code)
print("API Response:")
print(response.json())