import requests
import json
from datetime import date

class CartolaAPI:
    """ CartolaAPI - class to extract and handle data from the CartolaFC site """

    url = "https://api.cartolafc.globo.com/atletas/mercado"

    def read_data(self):
        """ reads json data of actual round from CartolaFC API"""

        r = requests.get(self.url)
        self.data = json.loads(r.text)
        return self.data


    def save_rawdata(self, filename="", foldername=""):
        """ saves data as readed to csv file"""

        today = date.today()

        if foldername == "":
            foldername = "data" + str(today.year) + "/"

        if filename == "":
            filename = "cartola" + str(today.isoformat()) + ".txt"

        file = open(foldername + filename, 'w', encoding='utf8')
        file.write(json.dumps(self.data))
        file.close()

        return (foldername+filename)

    def load_rawdata(self, filename="", foldername=""):
        """ loads data from csv file"""

        if filename == "":
            return False

        if foldername == "":
            today = date.today()
            foldername = "data" + str(today.year) + "/"

        with open(foldername + filename) as json_data:
            self.data = json.load(json_data)
            json_data.close()
            return True

cartola_api = CartolaAPI()