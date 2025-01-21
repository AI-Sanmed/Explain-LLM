import requests
import json

test_data = {
    "ID": "1",
    "CAC": 20,
    "CTAI": 90.0,
    "NoduleSize": 4,
    "FollowUpCompare": "首次"
}

headers = {"Content-Type": "application/json"}
response = requests.post(
    "http://172.16.43.57:8005/explain_llm",
    json=test_data,
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print(result['response'])
else:
    print(f"Error: {response.text}")