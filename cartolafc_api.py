import requests
import json
from datetime import date


COD_TECNICO = 6


class CartolaAPI:

    """ CartolaAPI - class to extract and handle data from the CartolaFC site """
    game_over: bool

    urlmarket = "https://api.cartolafc.globo.com/atletas/mercado"
    urlmatches = "https://api.cartolafc.globo.com/partidas/"
    urlstatus = "https://api.cartolafc.globo.com/mercado/status"
    round = 0

    def read_data(self):
        """ reads json data of actual round from CartolaFC API"""
        r = requests.get(self.urlmarket)
        self.data = json.loads(r.text)
        return self.data

    def read_rounddata(self, r=0):
        """ reads json data of matches of a specific round r from CartolaFC API"""
        if (r >= 1) and (r <= 38):
            strround = str(r)
        else:
            strround = ""

        r = requests.get(self.urlmatches+strround)
        self.matchesdata = json.loads(r.text)
        return self.matchesdata

    def read_status_data(self):
        """ reads json data of general status info from CartolaFC API"""
        if self.round == 0:
            r = requests.get(self.urlstatus)
            status = json.loads(r.text)
            self.round = status["rodada_atual"]
            self.market_status = status["status_mercado"] # 1 Aberto, 2 Fechado
            self.game_over = status["game_over"] # True acabou a temporada
            self.season = status["temporada"]
        return self.season, self.round, self.market_status, self.game_over

    def save_rawdata(self, filename="", foldername=""):
        """ saves data as readed to csv file"""
        self.read_status_data()

        if foldername == "":
            foldername = "data" + str(self.season) + "/"

        if filename == "":
            filename = "mercado_" + str(self.season) + "_" + str(self.round) + ".txt"

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
            return self.data

cartola_api = CartolaAPI()