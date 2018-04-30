import pandas as pd

from cartolafc_api import cartola_api

# Scouts and points
#
#   A   5.0     Assitencia
#   CA  -2.0    Cartao amarelo
#   CV  -5.0    Cartao vermelho
#   DD  3.0     Defesa dificil (somente goleiro)
#   FC  -0.5    Falta cometida
#   FD  1.2     Finalizacao Defendida
#   FF  0.8     Finalizacao para Fora
#   FS  0.5     Falta sofrida
#   FT  3.0     Finalizacao na Trave
#   G   8.0     Gol
#   GC  -5.0    Gol Contra
#   GS  -2.0    Gol Sofrido (somente goleiro)
#   I   -0.5    Impedimento
#   PE  -0.3    Passe errado
#   RB  1.5     Roubada de Bola
#   SG  5.0     Jogo Sem sofrer Gol
#   ??  -4.0    Penalti perdido
#   ??  7.0     Defesa de penalti

class Cartoleiro:
    """ Cartoleiro - encapsulate teams and players stats for team building """

    next_round = None
    rounds = None
    scout_table = pd.DataFrame()
    rounds_table = pd.DataFrame()

    def __init__(self):
        """ init teams data reading teams data from CartolaAPI """
        self.df_teams = self.read_teams()
        self.read_last_round()
        self.read_last_round()

    @classmethod
    def read_teams(self):
        """ reads teams data from CartolaAPI to a DataFrame
        :return: DataFrame with all teams from the championship
        """
        df = pd.DataFrame(cartola_api.read_rounddata()["clubes"]).T
        df.loc['293'].abreviacao = "CAP"  # adjust alias to avoid ambiguous identification
        return df

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
        self.scout_table.to_csv("data2018/scout_table.csv", encoding='utf_16')
        return self.scout_table

    def read_last_round(self):
        if self.rounds_table.shape[0] == 0:
            round = 1
        else:
            round = self.rounds_table['rodada_id'].max() + 1
        df = pd.DataFrame(cartola_api.read_rounddata(round)['partidas'])
        df['rodada_id'] = round
        self.rounds_table = self.rounds_table.append(df)
        self.rounds_table.to_csv("data2018/rounds_table.csv", encoding='utf_16')
        return self.rounds_table