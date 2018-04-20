import pandas as pd

from cartolafc_api import cartola_api


class Cartoleiro:
    """ Cartoleiro - encapsulate teams and players stats for team building """

    next_round = None
    rounds = None
    scout_table = pd.DataFrame()

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


    def update_scout(self):
        df_atletas = pd.DataFrame(cartola_api.read_data()['atletas'])
        #scouts = pd.DataFrame()
        l = []
        for index, atleta in df_atletas.iterrows():
            d = atleta['scout']
            d['atleta_id'] = atleta['atleta_id']
            d['rodada_id'] = atleta['rodada_id']
            d['apelido'] = atleta['apelido']
            d['clube_id'] = atleta['clube_id']
            d['jogos_num'] = atleta['jogos_num']
            d['media_num'] = atleta['media_num']
            d['pontos_num'] = atleta['pontos_num']
            d['posicao_id'] = atleta['posicao_id']
            d['preco_num'] = atleta['preco_num']
            d['status_id'] = atleta['status_id']
            d['variacao_num'] = atleta['variacao_num']
            l.append(d)
        self.scout_table = self.scout_table.append(l)

        self.scout_table = self.scout_table.set_index(['rodada_id', 'atleta_id'])
        self.scout_table.to_csv("data2018/scout_table.csv")
        return self.scout_table