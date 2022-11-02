from operator import itemgetter  # itemgetter used to sort dictionary items
import pandas as pd
from cartolafc_api import cartola_api
import cartoleiro

# constants
i_total = 0
i_home = 1
i_guest = 2

# rounds - global collection to store every round of matches
rounds = {}

points = {}  # key = team  value = [total points, points as host, points as guest]

plays = {}  # key = team value = [total plays, plays as host, plays as guest]

performs = {}
no_goals_received = {}  # games that team suffer no goals: total, as host, as guest
top_goals_scored = {}
goals_scored = {}
goals_suffered = {}
idx_goals_attack = {}
idx_goals_defense = {}
idx_coach = {}
idx_goalkeeper = {}


def create_team_list(ref_round, team_list):
    """ creates an empty team list to populate with metrics"""
    for match in ref_round:
        team_list[match["host"]] = [0, 0, 0]
        team_list[match["guest"]] = [0, 0, 0]


def calculate_performance():
    """ calculates team s performance based on points earned per points matched"""
    for team in plays.keys():
        performs[team] = [0, 0, 0]
        for i in range(3):
            performs[team][i] = points[team][i] / (plays[team][i] * 3)


def count_no_goals_received():
    """ count the number of plays a teams have with no goals suffered"""
    if no_goals_received == {}:
        create_team_list(rounds["1"], no_goals_received)
    for match_round in rounds:
        for match in rounds[match_round]:
            if match["guest score"] == 0:
                no_goals_received[match["host"]][i_total] += 1
                no_goals_received[match["host"]][i_home] += 1
            if match["host score"] == 0:
                no_goals_received[match["guest"]][i_total] += 1
                no_goals_received[match["guest"]][i_guest] += 1


def count_goals_scorered():
    """Count the number of goal scored for each team on the played rounds of the league"""
    if goals_scored == {}:
        create_team_list(rounds["1"], goals_scored)
    for match_round in rounds:
        for match in rounds[match_round]:
            goals_scored[match["guest"]][i_total] += match["guest score"]
            goals_scored[match["guest"]][i_guest] += match["guest score"]
            goals_scored[match["host"]][i_total] += match["host score"]
            goals_scored[match["host"]][i_home] += match["host score"]


def calc_idx_goals_attack(match_round):
    """Calculate an index for each team based on the match_round to rank the best options on attack"""
    if idx_goals_attack == {}:
        create_team_list(rounds["1"], idx_goals_attack)
    for match in match_round:
        idx_goals_attack[match["host"]][i_total] = goals_scored[match["host"]][i_home] / \
                                                   plays[match["host"]][i_home] * \
                                                   goals_suffered[match["guest"]][i_guest] / \
                                                   plays[match["guest"]][i_guest]
        idx_goals_attack[match["guest"]][i_total] = goals_scored[match["guest"]][i_guest] / \
                                                    plays[match["guest"]][i_guest] * \
                                                    goals_suffered[match["host"]][i_home] / \
                                                    plays[match["host"]][i_home]

    idx_sum = 0
    for item in idx_goals_attack.items():
        idx_sum += item[1][i_total]
    for item in idx_goals_attack.items():
        idx_goals_attack[item[0]][i_total] = item[1][i_total] / idx_sum


def calc_idx_coach(match_round):
    """Calculate an index for each team combining attack and defense indexes to rank coaches for the round"""
    if idx_coach == {}:
        create_team_list(rounds["1"], idx_coach)
    idx_sum = 0
    for team in plays.keys():
        idx_coach[team][i_total] = idx_goals_defense[team][i_total] * idx_goals_attack[team][i_total]
        idx_sum += idx_coach[team][i_total]

    for item in idx_coach.items():
        idx_coach[item[0]][i_total] = item[1][i_total] / idx_sum


def calc_idx_goalkeeper(match_round):
    """Calculate an index to rank goalkeeper for the round"""
    if idx_goalkeeper == {}:
        create_team_list(rounds["1"], idx_goalkeeper)
    for match in match_round:
        idx_goalkeeper[match["host"]][i_total] = idx_goals_defense[match["host"]][i_total] * \
                                                 (idx_goals_attack[match["guest"]][i_total] ** 2) * \
                                                 no_goals_received[match["host"]][i_total]

        idx_goalkeeper[match["guest"]][i_total] = (idx_goals_defense[match["guest"]][i_total] ** 2) * \
                                                  idx_goals_attack[match["host"]][i_total] * \
                                                  no_goals_received[match["guest"]][i_total]
    idx_sum = 0
    for item in idx_goalkeeper.items():
        idx_sum += item[1][i_total]
    for item in idx_goalkeeper.items():
        idx_goalkeeper[item[0]][i_total] = item[1][i_total] / idx_sum


def calc_idx_goals_defense(match_round):
    """Calculate an index for each team based on the next match_round to rank the best options on defense"""
    if idx_goals_defense == {}:
        create_team_list(rounds["1"], idx_goals_defense)
    for match in match_round:
        idx_goals_defense[match["host"]][i_total] = 1 / ((goals_suffered[match["host"]][i_home] /
                                                          plays[match["host"]][i_home]) *
                                                         (goals_scored[match["guest"]][i_guest]) /
                                                         plays[match["guest"]][i_guest])
        idx_goals_defense[match["guest"]][i_total] = 1 / ((goals_suffered[match["guest"]][i_guest] /
                                                           plays[match["guest"]][i_guest]) *
                                                          (goals_scored[match["host"]][i_home] /
                                                           plays[match["host"]][i_home]))

    idx_sum = 0
    for item in idx_goals_defense.items():
        idx_sum += item[1][i_total]
    for item in idx_goals_defense.items():
        idx_goals_defense[item[0]][i_total] = item[1][i_total] / idx_sum


def count_goals_suffered():
    """Count the number of goal suffered for each team on the played rounds of the league"""
    if goals_suffered == {}:
        create_team_list(rounds["1"], goals_suffered)
    for match_round in rounds:
        for match in rounds[match_round]:
            goals_suffered[match["guest"]][i_total] += match["host score"]
            goals_suffered[match["guest"]][i_guest] += match["host score"]
            goals_suffered[match["host"]][i_total] += match["guest score"]
            goals_suffered[match["host"]][i_home] += match["guest score"]


def count_top_scorer(top_score):
    """ calculates de the number of plays in witch a team scores more or equal to top_score goals"""
    if top_goals_scored == {}:
        create_team_list(rounds["1"], top_goals_scored)
    for match_round in rounds:
        for match in rounds[match_round]:
            if match["guest score"] >= top_score:
                top_goals_scored[match["guest"]][i_total] += 1
                top_goals_scored[match["guest"]][i_guest] += 1
            if match["host score"] >= top_score:
                top_goals_scored[match["host"]][i_total] += 1
                top_goals_scored[match["host"]][i_home] += 1


def calculate_teams_points():
    """ calculate de number of points a team earned on the league"""
    if points == {}:
        create_team_list(rounds["1"], points)
    if plays == {}:
        create_team_list(rounds["1"], plays)

    for match_round in rounds:
        for match in rounds[match_round]:
            plays[match["host"]][i_total] += 1
            plays[match["host"]][i_home] += 1  # add play as host
            plays[match["guest"]][i_total] += 1
            plays[match["guest"]][i_guest] += 1  # add play as guest
            if match["host score"] == match["guest score"]:
                points[match["host"]][i_total] += 1
                points[match["guest"]][i_total] += 1
                points[match["host"]][i_home] += 1
                points[match["guest"]][i_guest] += 1
            elif match["host score"] > match["guest score"]:
                points[match["host"]][i_total] += 3
                points[match["host"]][i_home] += 3
            else:
                points[match["guest"]][i_total] += 3
                points[match["guest"]][i_guest] += 3


def read_round_results(file_name):
    """ loads matches from files and store on rounds collection"""
    try:
        rodada = open(file_name, 'r', encoding='utf8')
        header = rodada.readline().split(" ")
        round_num = header[1].strip()
        match_round = []
        for line in rodada:
            match = {}
            match["date"] = line.strip()
            line = rodada.readline()
            match["host"] = line.strip()
            line = rodada.readline()
            match["guest"] = line.strip()
            line = rodada.readline()
            score = line.split(":")
            match["host score"] = int(score[0])
            match["guest score"] = int(score[1])
            match_round.append(match)

        rodada.close()
        rounds[round_num] = match_round

    except FileNotFoundError:
        print("Erro ao abrir arquivo:", file_name)


def read_league_results(num_rounds):
    """ reads results from the league from beginning until the num_rounds round"""
    for i in range(num_rounds):
        read_round_results("resultados_rodada" + str(i + 1))


def read_next_round_file(file_name):
    """ reads the matches form the next round of the league"""
    try:
        file = open(file_name, 'r', encoding='utf8')
        file.readline().split(" ")
        # round_num = header[1].strip()
        match_round = []
        for line in file:
            match = {}
            match["date"] = line.strip()
            line = file.readline()
            match["host"] = line.strip()
            line = file.readline()
            match["guest"] = line.strip()
            match_round.append(match)

        file.close()
        return match_round

    except FileNotFoundError:
        print("Erro ao abrir arquivo:", file_name)


def print_sorted_table(table):
    """ prints the dictionary ordered by the indexes """
    list_to_print = sorted(table.items(), key=itemgetter(1), reverse=True)
    pos = 1
    for item in list_to_print:
        print(format(pos, "02n") + " " + format(item[0], "12s") + " " + str(item[1]))
        pos += 1


def save_classification():
    """ saves actual classification of the league on a file"""
    list_to_save = sorted(points.items(), key=itemgetter(1), reverse=True)
    try:
        file_classif = open("classificacao_geral", 'w', encoding='utf8')
        pos = 1
        for item in list_to_save:
            # print(format(pos, "02n")+ " " + format(item[0], "12s") + " " + str(item[1]) + " " + str(plays[item[0]]) +
            #      " " + format(performs[item[0]][0],".3f"))
            file_classif.write(format(pos, "02n") + " " + format(item[0], "12s") + " " + str(item[1][0]) + " "
                               + str(plays[item[0]][0]) + "\n")
            pos += 1
        file_classif.close()
    except FileExistsError:
        print("Erro ao salvar arquivo:", "classificacao_geral")


def formation_analysis(defense, attack):
    """Calculates the possible points for a specific defense/attack formation"""

    total_games_played = 0
    total_goals_scored = 0
    total_no_goals = 0
    for team in plays.keys():
        total_games_played += plays[team][i_total]
        total_goals_scored += goals_scored[team][i_total]
        total_no_goals += no_goals_received[team][i_total]

    points = (float(total_goals_scored) / float(total_games_played) * 8 * attack) + \
             (float(total_no_goals) / float(total_games_played) * 5 * (defense + 1))

    print("Pontos para " + str(defense) + " defensores e " + str(attack) + " atacantes: " + str(points))
    return points



def main():
    # console setup
    pd.set_option("display.width", None)

    # test if season is open, if not opened then load data from files

    cartola_data = cartola_api.read_data()
    season, round, market_st, game_over = cartola_api.read_status_data()

    # if last round and market is closed (4) then there is no more plays on this season
    #if cartola_data["rodada_atual"] == 38 and cartola_data["status_mercado"] == 4:
    if game_over:
        season_on = False
        print("Temporada ainda não começou :(")
        # load data from last round of the last season
        df_atletas = pd.read_csv("data" + str(season - 1) + "/rodada_38.csv", encoding="cp860")
    else:
        season_on = True
        print("Temporada aberta. Vamos jogar!")
        print("Dados salvos em: " + cartola_api.save_rawdata())
        df_atletas = pd.DataFrame(cartola_data["atletas"])
        df_atletas.to_csv("data" + str(season) + "/atletas.csv", encoding="cp860", errors="replace")

        df_status = pd.DataFrame(cartola_data["status"])
        df_posicoes = pd.DataFrame(cartola_data["posicoes"])

    df_atletas = df_atletas.set_index("atleta_id")

    # TODO include the above df_atletas load to the cartoleiro._init_ method
    cart = cartoleiro.Cartoleiro(season_on)

    # before next round calculations update tables Rounds e Scouts from last round
    if round >= 2:
        cart.update_scout(round-1)
        cart.update_rounds(round-1)

    # test to identify season first rounds
    if round <= 2:
        first_rounds = True
    else:
        first_rounds = False

    # prepare players dataframe to calcs

    df_comp = df_atletas
    # decode id to meaninful names
    if season_on: # TODO create a teams dictionary to substitute df_teams, df_posicoes and df_status need
        df_comp["team"] = df_comp["clube_id"].apply(lambda x: cart.df_teams.loc[str(x)].abreviacao)
        df_comp["pos"] = df_comp["posicao_id"].apply(lambda x: df_posicoes[str(x)]["abreviacao"])
        df_comp["status"] = df_comp["status_id"].apply(lambda x: df_status[str(x)]["nome"])

    # keep only players confirmed for the round (status_id == 7) and players in doubt to play (status_id == 2)
    df_comp = df_comp[df_comp.status_id == 7].append(df_comp[df_comp.status_id == 2])


    if not first_rounds: # calculate players stats for team selection
        cart.calc_ranking()
        cart.calc_round_indexes()

        pre_team = []
        coach_team = []

        goalkeeper_param = {"label": "GOLEIROS", "code": 1, "idx": "idx_defense", "qty": 3, "qty_bk": 1} # "idx_goalkeeper"
        attack_param = {"label": "ATACANTES", "code": 5, "idx": "idx_attack", "qty": 7, "qty_bk": 2}
        defense_param = {"label": "ZAGUEIROS", "code": 3, "idx": "idx_defense", "qty": 5, "qty_bk": 2}
        midfield_param = {"label": "MEIAS", "code": 4, "idx": "idx_attack", "qty": 7, "qty_bk": 2}
        sidefield_param = {"label": "LATERAIS", "code": 2, "idx": "idx_coach", "qty": 5, "qty_bk": 2}
        coach_param = {"label": "TÉCNICOS", "code": 6, "idx": "idx_coach", "qty": 5, "qty_bk": 0}
        columns_to_print = ["abreviacao", "apelido", "pos_pts", "preco_num", "media_num", "roi", "status_id"]

        team_list = []
        for param in [goalkeeper_param, attack_param, defense_param, midfield_param, sidefield_param, coach_param]:
            rank_players = cart.select_players(df_comp, param["code"], param["idx"])
            if param["code"] != 6:
                coach_team.append(rank_players)
                param["players"] = coach_team[-1].head(param["qty"])
                team_list.append((param["players"]["media_num"].mean(), param))
                pre_team.append(param["players"])
                param["ranked"] = rank_players
                #lowest_price = min(param["players"]["preco_num"])
                #df2 = rank_players.drop(param["players"].index)
                #df3 = df2.drop(df2[df2.preco_num > lowest_price].index)
                #param["subst"] = df3.head(param["qty_bk"])

            else:
                # special calculation for coaches, must be the last iteration on this loop. Need all other players agregated
                df_pos = pd.concat(coach_team)
                df_pos = df_pos.reset_index()
                df_pos.columns.values[0] = "clube_id"
                df_pos = df_pos[["clube_id", "media_num", "pos_pts"]].dropna()
                df_pos["pos_pts"] = df_pos["pos_pts"].astype("float")
                df_mean_team = df_pos.groupby("clube_id").mean(numeric_only=True)
                rank_players = rank_players.join(df_mean_team, lsuffix="_coach", rsuffix="_groupby")
                param["players"] = rank_players.sort_values("pos_pts_groupby", ascending=False).head(param["qty"])

        team_list.sort(reverse=True)
        for rank, param in team_list:
            print("* " + param["label"] + " ****************************************************************** média = " + "{:.2f}".format(rank))
            print(param["players"][columns_to_print])
            #print("- banco --------------------------------------------------------------------")
            #print(param["subst"][columns_to_print])
            #print()
        print("* " + coach_param["label"] + " **************************************************************************")
        print(coach_param["players"][
                  ["abreviacao", "apelido", "pos_pts_groupby", "preco_num", "media_num_groupby", "roi", "status_id"]])
        print()
        team_list.append((0, coach_param))

        budget = 140.43
        my_team = cart.assemble_team(budget, team_list)
        # now we select the best option for bench
        for param in [goalkeeper_param, attack_param, defense_param, midfield_param, sidefield_param]:
            max_price = my_team[param["code"]]["cheapest"]
            if my_team[param["code"]]["all_confirmed"]:
                my_team[param["code"]]["bench"] = param["ranked"].loc[param["ranked"]["preco_num"] < max_price].head(1)
            else:
                my_team[param["code"]]["bench"] = param["ranked"].loc[(param["ranked"]["preco_num"] < max_price) &
                                                                      (param["ranked"]["status_id"] != 2)].head(1)

        print("CAPITÃES")
        df_selected = pd.concat(pre_team)
        df_selected = df_selected.set_index("atleta_id")
        selected_list = df_selected.index
        df_players_temp = cart.scout_table
        df_players_list = df_players_temp.set_index(["atleta_id", "rodada_id"])
        df_players_list = df_players_list.loc[selected_list, :]
        df_captains = pd.DataFrame()
        for player in df_players_list.index.get_level_values(0).unique():
            # .copy(deep=True) to supress SettingWithCopyWarning
            df = df_players_temp[df_players_temp.atleta_id == player].copy(deep=True)
            # test to flag the player who plays in a specific round
            df["jogou"] = (df["jogos_num"].diff() != 0) & (df["jogos_num"] != 0)
            df_captains = pd.concat([df_captains, df], axis=0)
        # discard rows where player didnt play the match
        df_captains = df_captains[df_captains.jogou][["atleta_id", "pontos_num"]]

        df_captains = df_captains.groupby("atleta_id").median()
        df_captains = df_selected.join(df_captains, lsuffix="_player", rsuffix="_median")
        df_captains = df_captains.sort_values("pontos_num_median", ascending=False)
        print(df_captains[["team", "apelido", "pontos_num_median"]].head(8))

        cart.get_captain(df_captains, my_team) # select the best median player in my team as a captain

        cart.print_my_team(my_team, budget) # print my full team selected for the round

    else: # select players using price difference between the last and actual seasons
        print('Primeiras rodadas, vamos escolher os jogadores em relação ao preço que terminaram a temporada passada...')

        # read data from last season to compare
        # df_players_last_season = pd.read_csv("data" + str(season - 1) + "/rodada_38.csv", encoding="cp860")
        cartola_prev = cartola_api.load_rawdata("mercado_2021_38.txt", "data2021/")


        df_players_last_season = pd.DataFrame(cartola_prev["atletas"])
        df_players_last_season = df_players_last_season.set_index("atleta_id")

        pre_team = []

        i = 0
        print("GOLEIROS")
        pre_team.append(cart.select_players_pricediff(df_comp, 1, df_players_last_season, home_only=True).head(3))
        print(pre_team[i][["team", "apelido_actual", "dif_preco", "preco_num_actual", "preco_num_last",
                           "media_num_last", "var_preco"]])
        i += 1
        print("ATACANTES")
        pre_team.append(cart.select_players_pricediff(df_comp, 5, df_players_last_season, home_only=True).head(7))
        print(pre_team[i][["team", "apelido_actual", "dif_preco", "preco_num_actual", "preco_num_last",
                           "media_num_last", "var_preco"]])

        i += 1
        print("ZAGUEIROS")
        pre_team.append(cart.select_players_pricediff(df_comp, 3, df_players_last_season, home_only=True).head(5))
        print(pre_team[i][["team", "apelido_actual", "dif_preco", "preco_num_actual", "preco_num_last",
                           "media_num_last", "var_preco"]])

        i += 1
        print("MEIAS")
        pre_team.append(cart.select_players_pricediff(df_comp, 4, df_players_last_season, home_only=True).head(7))
        print(pre_team[i][["team", "apelido_actual", "dif_preco", "preco_num_actual", "preco_num_last",
                           "media_num_last", "var_preco"]])

        i += 1
        print("LATERAIS")
        pre_team.append(cart.select_players_pricediff(df_comp, 2, df_players_last_season, home_only=True).head(5))
        print(pre_team[i][["team", "apelido_actual", "dif_preco", "preco_num_actual", "preco_num_last",
                           "media_num_last", "var_preco"]])

        print("TECNICOS")
        df_coaches = cart.select_players_pricediff(df_comp, 6, df_players_last_season, home_only=True)
        df_coaches = df_coaches.set_index("clube_id_actual")[["team", "apelido_actual", "preco_num_actual"]]
        df_pos = df_comp.join(df_players_last_season, lsuffix="_actual", rsuffix="_last")
        df_pos = df_pos[["clube_id_actual", "media_num_last"]].dropna()
        # df_pos = df_pos.replace({"#CAMPO!":None})
        df_pos["media_num_last"] = df_pos["media_num_last"].astype("float")
        df_mean_last_conf = df_pos.groupby("clube_id_actual").mean(numeric_only=True)
        df_coaches = df_coaches.join(df_mean_last_conf)
        print(df_coaches.sort_values("media_num_last", ascending=False).head(5))

        print("CAPITÃES")
        df_selected = pd.concat(pre_team)
        df_selected["mean_of_means"] = (df_selected["media_num_last"].astype("float") + df_selected["media_num_actual"])/2
        print(df_selected.sort_values("mean_of_means", ascending=False)[["team", "apelido_actual",
                                                                                  "mean_of_means"]].head(5))

main()
