from operator import itemgetter
"""itemgetter used to sort dictionary items"""

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
        idx_goals_defense[match["host"]][i_total] = 1 / ((goals_suffered[match["host"]][i_home] / \
                                                          plays[match["host"]][i_home]) *
                                                   (goals_scored[match["guest"]][i_guest]) / \
                                                         plays[match["guest"]][i_guest])
        idx_goals_defense[match["guest"]][i_total] = 1 / ((goals_suffered[match["guest"]][i_guest] / \
                                                           plays[match["guest"]][i_guest]) *
                                                    (goals_scored[match["host"]][i_home] / \
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


    print ("Pontos para " + str(defense) + " defensores e " + str(attack) + " atacantes: " + str(points))
    return points



def main():
    """ the main funtion :) """

    # load results from the first n rounds of league
    num_round = 25
    print("Lendo os resultados dos jogos das " + str(num_round) + " rodadas...")
    read_league_results(num_round)

    print("Calculando os pontos ganhos...")
    calculate_teams_points()

    # for line in teams:
    #    print(line, ":", teams[line])
    print("Calculando o aproveitamento...")
    calculate_performance()

    print("Calculando jogos sem sofrer gols...")
    count_no_goals_received()
    print("Calculando jogos marcando mais que X gols...")
    count_top_scorer(3)
    print("Calculando gols marcados...")
    count_goals_scorered()
    print("Calculando gols sofridos...")
    count_goals_suffered()

    print("Gravando a classificação em arquivo...")
    save_classification()

    print("Carregando jogos da próxima rodada...")
    next_round = read_next_round_file('jogos_rodada26')

    print("Calculando índice de ataque baseado em gols...")
    calc_idx_goals_attack(next_round)

    print("\n")
    print("-- Melhores times para escalar Atacantes:")
    print("\n")
    print_sorted_table(idx_goals_attack)


    print("Calculando índice de defesa baseado em gols...")
    calc_idx_goals_defense(next_round)
    print("\n")
    print("-- Melhores times para escalar Defensores:")
    print("\n")
    print_sorted_table(idx_goals_defense)

    print("Calculando índice de técnico...")
    calc_idx_coach(next_round)
    print("\n")
    print("-- Melhores times para escalar Técnicos:")
    print("\n")
    print_sorted_table(idx_coach)

    print("\n")
    print("Calculando índice de goleiro...")
    calc_idx_goalkeeper(next_round)
    print("\n")
    print("-- Melhores times para escalar Goleiro:")
    print("\n")
    print_sorted_table(idx_goalkeeper)

    print("\n")
    formation_analysis(3, 7)
    formation_analysis(4, 6.5)


main()
