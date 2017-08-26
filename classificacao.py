# rounds - global collection to store every round of matches
rounds = {}

teams = {}


def create_team_list(ref_round):
    for match in ref_round:
        teams[match["host"]] = 0
        teams[match["guest"]] = 0


def calculate_teams_points():
    if teams == {}:
        create_team_list(rounds["1"])

    for round in rounds:
        for match in rounds[round]:
            if match["host score"] == match["guest score"]:
                teams[match["host"]] += 1
                teams[match["guest"]] += 1
            elif match["host score"] > match["guest score"]:
                teams[match["host"]] += 3
            else:
                teams[match["guest"]] += 3


# ler_arquivo_resultados
# function to load matches from files anda store on rounds collection
def ler_arquivo_resultados(file_name):
    try:
        rodada = open(file_name, 'r', encoding='utf8')
        header = rodada.readline().split(" ")
        round_num = header[1].strip()
        round = []
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
            round.append(match)


        rodada.close()
        rounds[round_num] = round

    except:
        print("Erro ao abrir arquivo:", file_name)


def save_classification():
    try:
        file_classif = open("classificacao_geral", 'w', encoding='utf8')
        for team, points in teams.items():
            print(format(team,"12s") + " " + str(points) + "\n")
            file_classif.write(format(team,"12s") + " " + str(points) + "\n")
        file_classif.close()
    except:
        print("Erro ao salvar arquivo:", "classificacao_geral")



def main():
    print("Aqui vai aparecer a classificação do campeonato brasileiro!")
    ler_arquivo_resultados('resultados_rodada1')
    ler_arquivo_resultados('resultados_rodada2')
    ler_arquivo_resultados('resultados_rodada3')
    ler_arquivo_resultados('resultados_rodada4')
    ler_arquivo_resultados('resultados_rodada5')
    ler_arquivo_resultados('resultados_rodada6')
    ler_arquivo_resultados('resultados_rodada7')
    ler_arquivo_resultados('resultados_rodada8')
    ler_arquivo_resultados('resultados_rodada9')
    ler_arquivo_resultados('resultados_rodada10')
    ler_arquivo_resultados('resultados_rodada11')
    ler_arquivo_resultados('resultados_rodada12')
    ler_arquivo_resultados('resultados_rodada13')
    ler_arquivo_resultados('resultados_rodada14')
    ler_arquivo_resultados('resultados_rodada15')
    ler_arquivo_resultados('resultados_rodada16')
    ler_arquivo_resultados('resultados_rodada17')
    ler_arquivo_resultados('resultados_rodada18')
    ler_arquivo_resultados('resultados_rodada19')
    ler_arquivo_resultados('resultados_rodada20')
    ler_arquivo_resultados('resultados_rodada21')

    #create_team_list(rounds["1"])
    calculate_teams_points()

    #for line in teams:
    #    print(line, ":", teams[line])
    print(teams)

    save_classification()


main()