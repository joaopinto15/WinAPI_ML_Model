import json

with open("datasets/api_map.json") as f:
    API_MAP = json.load(f)

def mapear_chamadas(lista):
    return [str(API_MAP.get(api, -1)) for api in lista]
