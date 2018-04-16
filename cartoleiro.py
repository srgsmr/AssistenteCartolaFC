import pandas as pd

from cartolafc_api import cartola_api


class Cartoleiro:
    """ Cartoleiro - encapsulate teams and players stats for team building """

    next_round = None
    rounds = None

    def __init__(self):
        """ init teams data reading teams data from CartolaAPI """
        self.teams_table = self.read_teams()

    @classmethod
    def read_teams(self):
        """ reads teams data from CartolaAPI to a DataFrame
        :return: DataFrame with all teams from the championship
        """
        df_teams = pd.DataFrame(cartola_api.read_rounddata()["clubes"]).T
        df_teams.loc['293'].abreviacao = "CAP"  # adjust alias to avoid ambiguous identification
        return df_teams

    def read_next_round(self):
        """ extract matches from the next round to next_round DataFrame """
        self.next_round = pd.DataFrame(cartola_api.read_rounddata()['partidas'])

        # removing columns aproveitamento_mandante aproveitamento_visitante clube_casa_posicao, clube_visitante_posicao
        self.next_round = self.next_round[['clube_casa_id', 'clube_visitante_id', 'local', 'partida_data',
                                           'partida_id', 'placar_oficial_mandante', 'placar_oficial_visitante',
                                           'url_confronto', 'url_transmissao', 'valida']]
