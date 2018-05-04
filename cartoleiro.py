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
    ranking = pd.DataFrame()

    def __init__(self):
        """ init teams data reading teams data from CartolaAPI """
        self.df_teams = self.read_teams()
        self.scout_table = pd.read_csv("data2018/scout_table.csv", encoding='utf_16')
        self.rounds_table = pd.read_csv("data2018/rounds_table.csv", encoding='utf_16')
        #self.read_last_round()
        #self.read_last_round()

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
        df_atletas = pd.DataFrame(cartola_api.data['atletas'])
        l = []
        for index, atleta in df_atletas.iterrows():
            #d = {}
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
        self.scout_table = pd.read_csv("data2018/scout_table.csv", encoding='utf_16')
        self.scout_table = self.scout_table.append(l)

        self.scout_table = self.scout_table.set_index(['rodada_id', 'atleta_id'])
        self.scout_table.to_csv("data2018/scout_table.csv", encoding='utf_16')
        return self.scout_table

    def update_rounds(self):
        if self.rounds_table.shape[0] == 0:
            round = 1
        else:
            round = self.rounds_table['rodada_id'].max() + 1
        df = pd.DataFrame(cartola_api.read_rounddata(round)['partidas'])
        df['rodada_id'] = round
        self.rounds_table = self.rounds_table.append(df)
        self.rounds_table.to_csv("data2018/rounds_table.csv", encoding='utf_16')
        return self.rounds_table

    def calc_ranking(self, top_score = 3):
        self.ranking = self.df_teams[["abreviacao", "id", "nome"]]
        self.ranking.set_index("id")
        self.ranking["host_matches"] = 0.0
        self.ranking["guest_matches"] = 0.0
        self.ranking["host_scored"] = 0.0
        self.ranking["guest_scored"] = 0.0
        self.ranking["host_suffered"] = 0.0
        self.ranking["guest_suffered"] = 0.0
        self.ranking["host_nogoals_suf"] = 0.0
        self.ranking["guest_nogoals_suf"] = 0.0

        for team_id in self.df_teams[["id"]].get_values():
            id = str(team_id[0])
            df_host = self.rounds_table.loc[self.rounds_table["clube_casa_id"] == team_id[0]]
            df_guest = self.rounds_table.loc[self.rounds_table["clube_visitante_id"] == team_id[0]]
            self.ranking.loc[id, "host_matches"] = df_host["clube_casa_id"].count()
            self.ranking.loc[id, "guest_matches"] = df_guest["clube_visitante_id"].count()
            self.ranking.loc[id, "host_scored"] = df_host["placar_oficial_mandante"].sum()
            self.ranking.loc[id, "guest_scored"] = df_guest["placar_oficial_visitante"].sum()
            self.ranking.loc[id, "host_suffered"] = df_host["placar_oficial_visitante"].sum()
            self.ranking.loc[id, "guest_suffered"] = df_guest["placar_oficial_mandante"].sum()
            self.ranking.loc[id, "host_nogoals_suf"] = df_host[df_host["placar_oficial_visitante"] == 0] \
                ["clube_casa_id"].count()
            self.ranking.loc[id, "guest_nogoals_suf"] = df_guest[df_guest["placar_oficial_mandante"] == 0] \
                ["clube_visitante_id"].count()
            self.ranking.loc[id, "host_topscore"] = df_host[df_host["placar_oficial_mandante"] >= top_score] \
                ["clube_casa_id"].count()
            self.ranking.loc[id, "guest_topscore"] = df_guest[df_guest["placar_oficial_visitante"] >= top_score] \
                ["clube_visitante_id"].count()
            df_host["points"] = df_host[df_host["placar_oficial_mandante"] == df_host["placar_oficial_visitante"]] \
                                ["clube_casa_id"].count() + \
                                df_host[df_host["placar_oficial_mandante"] > df_host["placar_oficial_visitante"]] \
                                ["clube_casa_id"].count() * 3
            self.ranking.loc[id, "host_points"] = df_host["points"].sum()
            df_guest["points"] = df_guest[df_guest["placar_oficial_mandante"] == df_guest["placar_oficial_visitante"]] \
                                ["clube_casa_id"].count() + \
                                 df_guest[df_guest["placar_oficial_mandante"] < df_guest["placar_oficial_visitante"]] \
                                ["clube_casa_id"].count() * 3
            self.ranking.loc[id, "guest_points"] = df_guest["points"].sum()

        self.ranking["total_matches"] = self.ranking["host_matches"] + self.ranking["guest_matches"]
        self.ranking["total_scored"] = self.ranking["host_scored"] + self.ranking["guest_scored"]
        self.ranking["total_suffered"] = self.ranking["host_suffered"] + self.ranking["guest_suffered"]
        self.ranking["total_nogoals_suf"] = self.ranking["host_nogoals_suf"] + self.ranking["guest_nogoals_suf"]
        self.ranking["total_topscore"] = self.ranking["host_topscore"] + self.ranking["guest_topscore"]
        self.ranking["total_points"] = self.ranking["host_points"] + self.ranking["guest_points"]
        self.ranking = self.ranking.sort_values("total_points", ascending=False)
        #print(self.ranking)

    def calc_round_indexes(self):
        self.read_next_round()
        self.indexes = self.df_teams[["abreviacao", "id", "nome"]]
        self.indexes.set_index("id")
        self.indexes["attack"] = None
        self.indexes["defense"] = 0.0

        for (host_id, guest_id) in self.next_round[["clube_casa_id", "clube_visitante_id"]].get_values():
            print("Mandante: " + str(host_id) + " Visitante: " + str(guest_id))
            host = str(host_id)
            guest = str(guest_id)
            self.indexes.loc[host, "attack"] = self.ranking.loc[host, "host_scored"] / \
                                               self.ranking.loc[host, "host_matches"] * \
                                               self.ranking.loc[guest, "guest_suffered"] / \
                                               self.ranking.loc[guest, "guest_matches"]
            self.indexes.loc[guest, "attack"] = self.ranking.loc[guest, "guest_scored"] / \
                                               self.ranking.loc[guest, "guest_matches"] * \
                                               self.ranking.loc[host, "host_suffered"] / \
                                               self.ranking.loc[host, "host_matches"]
            self.indexes.loc[host, "defense"] = 1 / (self.ranking.loc[host, "host_suffered"] / \
                                           self.ranking.loc[host, "host_matches"] * \
                                           self.ranking.loc[guest, "guest_scored"] / \
                                           self.ranking.loc[guest, "guest_matches"])
            self.indexes.loc[guest, "defense"] = 1 / (self.ranking.loc[guest, "guest_suffered"] / \
                                            self.ranking.loc[guest, "guest_matches"] * \
                                            self.ranking.loc[host, "host_scored"] / \
                                            self.ranking.loc[host, "host_matches"])
        total = self.indexes["attack"].sum()
        self.indexes["idx_attack"] = self.indexes["attack"] / total
        total = self.indexes["defense"].replace([float('inf')],[0]).sum()
        self.indexes["idx_defense"] = self.indexes["defense"] / total

        print(self.indexes.sort_values("idx_defense", ascending=False))

