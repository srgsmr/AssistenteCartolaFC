import pandas as pd

from cartolafc_api import cartola_api

class Cartoleiro:

    next_round = None
    rounds = None

    def __init__(self):
        self.teams_table = self.read_teams()

    def read_teams(self):
        df_teams = pd.DataFrame(cartola_api.read_rounddata()["clubes"]).T
        df_teams.loc['293'].abreviacao = "ATP"
        #df_teams["293"]["abreviacao"] = "ATP"  # adjust alias to avoid ambiguous identification
        return df_teams

    def read_next_round(self):
        self.next_round = pd.DataFrame(cartola_api.read_rounddata()['partidas'])

        #removing columns aproveitamento_mandante aproveitamento_visitante clube_casa_posicao, clube_visitante_posicao
        self.next_round = self.next_round[['clube_casa_id','clube_visitante_id', 'local', 'partida_data',
                                           'partida_id', 'placar_oficial_mandante', 'placar_oficial_visitante',
                                           'url_confronto', 'url_transmissao', 'valida']]