from operator import itemgetter

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


def create_team_list(ref_round, team_list):
    for match in ref_round:
        team_list[match["host"]] = [0, 0, 0]
        team_list[match["guest"]] = [0, 0, 0]
        # plays[match["host"]] = [0, 0, 0]
        # plays[match["guest"]] = [0, 0, 0]


def calculate_performance():
    for team in plays.keys():
        performs[team] = [0, 0, 0]
        for i in range(3):
            performs[team][i] = points[team][i] / (plays[team][i] * 3)


def count_no_goals_received():
    if no_goals_received == {}:
        create_team_list(rounds["1"], no_goals_received)
    for match_round in rounds:
        for match in rounds[match_round]:
            if match["guest score"] == 0:
                no_goals_received[match["host"]][0] += 1
                no_goals_received[match["host"]][1] += 1
            if match["host score"] == 0:
                no_goals_received[match["guest"]][0] += 1
                no_goals_received[match["guest"]][2] += 1


def count_goals_scorered():
    if goals_scored == {}:
        create_team_list(rounds["1"], goals_scored)
    for match_round in rounds:
        for match in rounds[match_round]:
            goals_scored[match["guest"]][0] += match["guest score"]
            goals_scored[match["guest"]][2] += match["guest score"]
            goals_scored[match["host"]][0] += match["host score"]
            goals_scored[match["host"]][1] += match["host score"]


def calc_idx_goals_attack(match_round):
    if idx_goals_attack == {}:
        create_team_list(rounds["1"], idx_goals_attack)
    for match in match_round:
        idx_goals_attack[match["host"]][0] = goals_scored[match["host"]][1] / plays[match["host"]][1] * \
                                             goals_suffered[match["guest"]][2] / plays[match["guest"]][2]
        idx_goals_attack[match["guest"]][0] = goals_scored[match["guest"]][2] / plays[match["guest"]][2] * \
                                              goals_suffered[match["host"]][1] / plays[match["host"]][1]


def calc_idx_goals_defense(match_round):
    if idx_goals_defense == {}:
        create_team_list(rounds["1"], idx_goals_defense)
    for match in match_round:
        idx_goals_defense[match["host"]][0] = 1 / ((goals_suffered[match["host"]][1] / plays[match["host"]][1]) *
                                                   (goals_scored[match["guest"]][2]) / plays[match["guest"]][2])
        idx_goals_defense[match["guest"]][0] = 1 / ((goals_suffered[match["guest"]][2] / plays[match["guest"]][2]) *
                                                    (goals_scored[match["host"]][1] / plays[match["host"]][1]))


def count_goals_suffered():
    if goals_suffered == {}:
        create_team_list(rounds["1"], goals_suffered)
    for match_round in rounds:
        for match in rounds[match_round]:
            goals_suffered[match["guest"]][0] += match["host score"]
            goals_suffered[match["guest"]][2] += match["host score"]
            goals_suffered[match["host"]][0] += match["guest score"]
            goals_suffered[match["host"]][1] += match["guest score"]


def count_top_scorer(top_score):
    if top_goals_scored == {}:
        create_team_list(rounds["1"], top_goals_scored)
    for match_round in rounds:
        for match in rounds[match_round]:
            if match["guest score"] >= top_score:
                top_goals_scored[match["guest"]][0] += 1
                top_goals_scored[match["guest"]][2] += 1
            if match["host score"] >= top_score:
                top_goals_scored[match["host"]][0] += 1
                top_goals_scored[match["host"]][1] += 1


def calculate_teams_points():
    if points == {}:
        create_team_list(rounds["1"], points)
    if plays == {}:
        create_team_list(rounds["1"], plays)

    for match_round in rounds:
        for match in rounds[match_round]:
            plays[match["host"]][0] += 1
            plays[match["host"]][1] += 1  # add play as host
            plays[match["guest"]][0] += 1
            plays[match["guest"]][2] += 1  # add play as guest
            if match["host score"] == match["guest score"]:
                points[match["host"]][0] += 1
                points[match["guest"]][0] += 1
                points[match["host"]][1] += 1
                points[match["guest"]][2] += 1
            elif match["host score"] > match["guest score"]:
                points[match["host"]][0] += 3
                points[match["host"]][1] += 3
            else:
                points[match["guest"]][0] += 3
                points[match["guest"]][2] += 3


# ler_arquivo_resultados
# function to load matches from files anda store on rounds collection
def read_round_results(file_name):
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
    for i in range(num_rounds):
        read_round_results("resultados_rodada" + str(i + 1))


def read_next_round_file(file_name):
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
    list_to_print = sorted(table.items(), key=itemgetter(1), reverse=True)
    pos = 1
    for item in list_to_print:
        print(format(pos, "02n") + " " + format(item[0], "12s") + " " + str(item[1]))
        pos += 1


def save_classification():
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


def main():
    # load results from the first n rounds of league
    read_league_results(22)

    calculate_teams_points()

    # for line in teams:
    #    print(line, ":", teams[line])
    calculate_performance()

    count_no_goals_received()
    count_top_scorer(3)
    count_goals_scorered()
    count_goals_suffered()

    save_classification()

    next_round = read_next_round_file('jogos_rodada23')

    calc_idx_goals_attack(next_round)
    print("--Melhores times para escalar Atacantes:")
    print_sorted_table(idx_goals_attack)

    print("\n")

    calc_idx_goals_defense(next_round)
    print("--Melhores times para escalar Defensores:")
    print_sorted_table(idx_goals_defense)


main()
