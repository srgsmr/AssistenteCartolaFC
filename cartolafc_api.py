import requests
import json

class CartolaAPI:
    """ CartolaAPI - class to extract and handle data from the CartolaFC site """

    url = "https://api.cartolafc.globo.com/atletas/mercado"

    def read_data(self):
        """ reads json data of actual round from CartolaFC API"""

        r = requests.get(self.url)
        self.data = json.loads(r.text)
        return self.data


    def save_rawdata(self, filename=""):
        """ saves data as readed to csv file"""

        if filename == "":
            filename = "data2018/cartola.txt"
        file = open(filename, 'w', encoding='utf8')
        file.write(json.dumps(self.data))
        file.close()

        return filename


cartola_api = CartolaAPI()