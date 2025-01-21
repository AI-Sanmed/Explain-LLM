import httpx
import json
import time

test_data = {
  "ID": "1234567890",
  "Name": "尹玉梅",
  "CAC": 20,
  "CTAI" : {
      "item1" : {
      "NoduleScore": 0.9,
      "NoduleType": "磨玻璃",
      "NoduleSize": 4,
      "NoduleDensity":220,
      "NoduleLocation": "左肺上叶"
    },
    "item2": {
        "NoduleScore": 0.8,
        "NoduleType": "混合型",
        "NoduleSize": 4,
        "NoduleDensity": 300,
        "NoduleLocation": "左肺上叶"
    }
  }
}

test_data_json = json.dumps(test_data)

headers = {"Content-Type": "application/json"}
with httpx.stream('POST', "http://172.16.43.57:8005/explain_chat", content=test_data_json, headers=headers, timeout=20) as r:
    for text in r.iter_text():
        if 'response' in text:
            text_part = text.split('{')[-1]
            text_json = json.loads('{' + text_part)
            print(text_json['response'], end='')