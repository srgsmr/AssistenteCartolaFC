import pandas as pd

from cartolafc_api import cartola_api

class Cartoleiro:

    next_round = None
    rounds = None

    def read_next_round(self):
        self.next_round = pd.DataFrame(cartola_api.read_rounddata()['partidas'])

        #removing columns aproveitamento_mandante aproveitamento_visitante clube_casa_posicao, clube_visitante_posicao
        self.next_round = self.next_round[['clube_casa_id','clube_visitante_id', 'local', 'partida_data',
                                           'partida_id', 'placar_oficial_mandante', 'placar_oficial_visitante',
                                           'url_confronto', 'url_transmissao', 'valida']]