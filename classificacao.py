from operator import itemgetter

# rounds - global collection to store every round of matches
rounds = {}

points = {}  #key = team  value = [total points, points as host, points as guest]

plays = {}    #key = team value = [total plays, plays as host, plays as guest]

performs = {}


def create_team_list(ref_round):
    for match in ref_round:
        points[match["host"]] = [0, 0, 0]
        points[match["guest"]] = [0, 0, 0]
        plays[match["host"]] = [0, 0, 0]
        plays[match["guest"]] = [0, 0, 0]


def calculate_performance():
    for team in plays.keys():
        performs[team] = [0, 0, 0]
        for i in range(3):
            performs[team][i] = points[team][i]/(plays[team][i]*3)





def calculate_teams_points():
    if points == {}:
        create_team_list(rounds["1"])

    for round in rounds:
        for match in rounds[round]:
            plays[match["host"]][0] += 1
            plays[match["host"]][1] += 1    #add play as host
            plays[match["guest"]][0] += 1
            plays[match["guest"]][2] += 1   #add play as guest
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
    list_to_save = sorted(points.items(), key=itemgetter(1), reverse=True)
    try:
        file_classif = open("classificacao_geral", 'w', encoding='utf8')
        pos = 1
        for item in list_to_save:
            print(format(pos, "02n")+ " " + format(item[0], "12s") + " " + str(item[1]) + " " + str(plays[item[0]])+ " " + format(performs[item[0]][0],".3f"))
            file_classif.write(format(pos, "02n")+ " " + format(item[0], "12s") + " " + str(item[1][0]) + " " + str(plays[item[0]][0])+ "\n")
            pos += 1
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
    ler_arquivo_resultados('resultados_rodada22')

    #create_team_list(rounds["1"])
    calculate_teams_points()

    #for line in teams:
    #    print(line, ":", teams[line])
    calculate_performance()

    save_classification()

    print(performs)

main()