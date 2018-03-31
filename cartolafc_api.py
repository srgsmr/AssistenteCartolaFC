import requests
import json

class CartolaAPI:
    # CartolaAPI - class to extract and handle data from the CartolaFC site

    url = "https://api.cartolafc.globo.com/atletas/mercado"

    def read_data(self):
        r = requests.get(self.url)
        data = json.loads(r.text, encoding="cp860")
        return data


cartola_api = CartolaAPI()