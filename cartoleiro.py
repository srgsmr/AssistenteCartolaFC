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


    def __init__(self, season_on=True):
        """ init teams data reading teams data from CartolaAPI """
        self.season_on = season_on
        if self.season_on:
            self.df_teams = self.read_teams()
        # TODO remove path hardcode to read these files
        try:
            self.scout_table = pd.read_csv("data2019/scout_table.csv", encoding='utf_16')
        except:
            self.scout_table = pd.DataFrame()

        try:
            self.rounds_table = pd.read_csv("data2019/rounds_table.csv", encoding='utf_16')
            # self.rounds_table = self.rounds_table[self.rounds_table['valida']==True]
        except:
            self.rounds_table = pd.DataFrame()
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


    def update_scout(self, round):

        if self.scout_table["rodada_id"].max() >= round:
            return self.scout_table

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
        self.scout_table = self.scout_table.append(l)

        self.scout_table = self.scout_table.set_index(['rodada_id', 'atleta_id'])
        self.scout_table.to_csv("data2019/scout_table.csv", encoding='utf_16')
        return self.scout_table

    def update_rounds(self, round):
        if not self.rounds_table.empty:
            if self.rounds_table["rodada_id"].max() >= round:
                return self.rounds_table

        df = pd.DataFrame(cartola_api.read_rounddata(round)['partidas'])
        df['rodada_id'] = round
        self.rounds_table = self.rounds_table.append(df)
        # TODO remove hardcoded path
        self.rounds_table.to_csv("data2019/rounds_table.csv", encoding='utf_16')
        return self.rounds_table

    def calc_ranking(self, top_score = 3):
        self.ranking = self.df_teams[["abreviacao", "id", "nome"]].copy(deep=True)
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
            df_host = self.rounds_table.loc[self.rounds_table["clube_casa_id"] == team_id[0]].copy(deep=True)
            df_guest = self.rounds_table.loc[self.rounds_table["clube_visitante_id"] == team_id[0]].copy(deep=True)
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

    def calc_round_indexes(self, cheating = None):
        self.read_next_round()
        self.indexes = self.df_teams[["abreviacao", "id", "nome"]].copy(deep=True)
        self.indexes.set_index("id")
        self.indexes["attack"] = None
        self.indexes["defense"] = 0.0
        self.indexes["goalkeeper"] = 0.0

        for (host_id, guest_id) in self.next_round[["clube_casa_id", "clube_visitante_id"]].get_values():
            host = str(host_id)
            guest = str(guest_id)
            self.indexes.loc[host, "attack"] = (max(0.5, self.ranking.loc[host, "host_scored"]) / \
                                               self.ranking.loc[host, "host_matches"]) * \
                                               (max(0.5, self.ranking.loc[guest, "guest_suffered"]) / \
                                               self.ranking.loc[guest, "guest_matches"])
            self.indexes.loc[guest, "attack"] = (max(0.5, self.ranking.loc[guest, "guest_scored"]) / \
                                               self.ranking.loc[guest, "guest_matches"]) * \
                                                (max(0.5, self.ranking.loc[host, "host_suffered"]) / \
                                               self.ranking.loc[host, "host_matches"])
            self.indexes.loc[host, "defense"] = max(0.1, self.ranking.loc[host, "host_nogoals_suf"]) / (max(0.5, self.ranking.loc[host, "host_suffered"]) / \
                                           self.ranking.loc[host, "host_matches"] * \
                                           max(0.5, self.ranking.loc[guest, "guest_scored"]) / \
                                           self.ranking.loc[guest, "guest_matches"])
            self.indexes.loc[guest, "defense"] = max(0.1, self.ranking.loc[guest, "guest_nogoals_suf"]) / (max(0.5, self.ranking.loc[guest, "guest_suffered"]) / \
                                            self.ranking.loc[guest, "guest_matches"] * \
                                            max(0.5, self.ranking.loc[host, "host_scored"]) / \
                                            self.ranking.loc[host, "host_matches"])
            self.indexes.loc[host, "goalkeeper"] = (self.indexes.loc[host, "defense"] * 3 + \
                                                   self.indexes.loc[guest, "attack"]) / 4 * \
                                                   max(0.1, self.ranking.loc[host, "total_nogoals_suf"])
            self.indexes.loc[guest, "goalkeeper"] = (self.indexes.loc[guest, "defense"] * 3 + \
                                                   self.indexes.loc[host, "attack"]) / 4 * \
                                                   max(0.1, self.ranking.loc[guest, "total_nogoals_suf"])
            # self.indexes.loc[host, "goalkeeper"] = self.indexes.loc[host, "defense"] * \
            #                                        (self.indexes.loc[guest, "attack"] ** 2) * \
            #                                        max(0.1, self.ranking.loc[host, "total_nogoals_suf"])
            # self.indexes.loc[guest, "goalkeeper"] = self.indexes.loc[guest, "defense"] * \
            #                                        (self.indexes.loc[host, "attack"] ** 2) * \
            #                                        max(0.1, self.ranking.loc[guest, "total_nogoals_suf"])

        total = self.indexes["attack"].sum()
        self.indexes["idx_attack"] = self.indexes["attack"] / total
        total = self.indexes["defense"].replace([float('inf')],[0]).sum()
        self.indexes["idx_defense"] = self.indexes["defense"] / total
        total = self.indexes["goalkeeper"].sum()
        self.indexes["idx_goalkeeper"] = self.indexes["goalkeeper"] / total
        self.indexes["idx_coach"] = (self.indexes["idx_attack"] + self.indexes["idx_defense"] * 2)/3

        for (host_id, guest_id) in self.next_round[["clube_casa_id", "clube_visitante_id"]].get_values():
            host = str(host_id)
            guest = str(guest_id)
            print(self.indexes["abreviacao"][host] + " (" +
                  "{:1.2f}".format(self.indexes["idx_attack"][host]) + "/"
                  "{:1.2f}".format(self.indexes["idx_defense"][host]) + "/"
                  "{:1.2f}".format(self.indexes["idx_goalkeeper"][host]) + "/"
                  "{:1.2f}".format(self.indexes["idx_coach"][host]) +
                  ") X (" +
                  "{:1.2f}".format(self.indexes["idx_attack"][guest]) + "/"
                  "{:1.2f}".format(self.indexes["idx_defense"][guest]) + "/"
                  "{:1.2f}".format(self.indexes["idx_goalkeeper"][guest]) + "/"
                  "{:1.2f}".format(self.indexes["idx_coach"][guest]) + ") " +
                  self.indexes["abreviacao"][guest])

    def select_players(self, df_players, position, idx):
        df_pos = df_players[df_players.posicao_id == position]
        # TODO create a formula for player selection by number of matches
        df_pos = df_pos[df_pos.jogos_num >= 5]

        df_pos.reset_index(level=0, inplace=True)
        df_pos = df_pos.set_index("clube_id")
        df_idx = self.indexes.set_index("id")
        df_pos = df_pos.join(df_idx, lsuffix="player", rsuffix="team")
        df_pos["pos_pts"] = df_pos["media_num"] * df_pos[idx]
        df_pos["roi"] = df_pos["pos_pts"] / df_pos["preco_num"]
        df_pos = df_pos.sort_values("pos_pts", ascending=False)
        return df_pos

    def select_players_pricediff(self, df_players, position, df_players_last_season, home_only=False):
        df_pos = df_players[df_players.posicao_id == position]
        # TODO create a formula for player selection by number of matches
        df_pos = df_pos[df_pos.jogos_num >= 0]

        df_pos_las = df_players_last_season
        # df_pos_las = df_players_last_season[df_players_last_season.posicao_id == position and
        #                                    df_players_last_season.jogos_num >= 25]

        if home_only and self.season_on:
            # keep only players from home teams for the next round
            self.read_next_round()
            df_pos = df_pos[df_pos.clube_id.isin(self.next_round["clube_casa_id"])]

        if self.season_on:
            a = 1
            # df_pos = df_pos.set_index("clube_id")
            # df_idx = self.indexes.set_index("id")
            # df_pos = df_pos.join(df_idx, lsuffix="player", rsuffix="team")
        else:
            df_pos.is_copy = False  # deactivate warning
            df_pos["abreviacao"] = df_pos["clube_id"]
            df_pos.is_copy = True   # reactivate warning

        df_pos = df_pos.join(df_pos_las, lsuffix="_actual", rsuffix="_last")

        df_pos["var_preco"] = df_pos["preco_num_last"] / df_pos["preco_num_actual"]
        df_pos["dif_preco"] = df_pos["preco_num_last"] - df_pos["preco_num_actual"]
        # df_pos["media_var_preco"] = df_pos["var_preco"] * df_pos["media_num"]

        df_pos = df_pos.sort_values("dif_preco", ascending=False)

        return df_pos


