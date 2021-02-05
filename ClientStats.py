from Defs import PlayerStats, get_stats, get_stat, titles, get_key, alphabet
import xlsxwriter
import requests
import json
import bs4

names = open("Names.txt", "r")

_names = []
for name in names:
    _names.append(name.split(":")[1][:-1])

def create_json(week: int):
    try:
        file = open(f"Week-{week}.json", "x")
    except:
        file = open(f"Week-{week}.json", "w")

    data = stats()
    to_dump = {}
    for player in data:
        to_dump[f"{player.name}"] = {f"Name": f"{player.name}", f"Tier": f"{player.tier}", f"Data": f"{player.stats}"}
    json.dump(to_dump, file)

def create_json_em(week: int):
    try:
        file = open(f"EM-Week-{week}.json", "x")
    except:
        file = open(f"EM-Week-{week}.json", "w")

    data = stats()
    to_dump = {}
    for player in data:
        if player.name in _names:
            to_dump[f"{player.name}"] = {f"Name": f"{player.name}", f"Tier": f"{player.tier}", f"Data": f"{player.stats}"}
    json.dump(to_dump, file)

def stats():
    link = "https://www.rocketsoccarconfederation.com/na/sx-stats/sx-player-stats/"
    tiers = "Premier,Master,Elite,Major,Minor,Challenger,Prospect,Contender,Amateur".split(",")
    table_min = 512  # 446
    _stats = []
    stats_names = []

    stats = []
    for tier in tiers:
        stats.append(bs4.BeautifulSoup(requests.get(link + f"/sx-{tier.lower()}-4").text, "lxml"))

    table_nums = [i for i in range(table_min, table_min + 9)]
    tables = []

    for num in table_nums:
        for stat in stats:
            info = stat.find(id=f"tablepress-{num}")
            if info is not None:
                tables.append(info)

    for a, table in enumerate(tables):

        table_sliced = None
        for i, _line in enumerate(table):
            if i == 3:
                table_sliced = str(_line).split("</tr>")

        for stats in table_sliced:
            name = get_stat(stats, "column-1")
            if name is None:
                continue
            _stats.append(PlayerStats(tiers[a], name, get_stats(stats)))
            stats_names.append(name)

    remove_duplicates(_stats, stats_names)

    return _stats

def remove_duplicates(_stats, stats_names):
    for name in stats_names:
        stats = []
        for stat in _stats:
            if stat.name == name:
                stats.append(stat)
        if len(stats) == 1:
            continue
        most_games, games = None, 0
        for stat in stats:
            if stat.games_played > games:
                games = stat.games_played
                most_games = stat
        for stat in stats:
            if stat != most_games:
                _stats.remove(stat)

def create_sheet(title, week):
    workbook = xlsxwriter.Workbook(f"{title}.xlsx")
    workbook.set_tab_ratio(50)
    sheet = workbook.add_worksheet(f"Week {week}")
    data = [i.get_info() for i in stats()]

    for i, t in enumerate(titles):
        sheet.write(f"{alphabet[i+1]}2", t)
        if i > 1:
            sheet.set_column(f"{alphabet[i + 1]}:{alphabet[i + 1]}", int(len(t) * 1.25))
        else:
            sheet.set_column(f"{alphabet[i + 1]}:{alphabet[i + 1]}", int(len(t) * 2.5))

    em_data = []
    for player in data:
        if player[0] in _names:
            em_data.append(player)

    for row, player in enumerate(em_data):
        for i, cell in enumerate(player):
            print(i, row)
            sheet.write(f"{alphabet[i + 1]}{row + 3}", cell)

    workbook.close()

def sort_rating():
    data = [i.get_info() for i in stats()]
    em_data = []
    for player in data:
        if player[0] in _names:
            em_data.append(player)
            print(player[0], player[8])
    scores = []
    for player in em_data:
        if player[10] > player[9]:
            scores.append([player[0], 2 * player[8] + player[10]])
        else:
            scores.append([player[0], 2 * player[8] + player[9]])
    sorted_scores = []

    for i in range(len(scores)):
        highest, highest_score = None, 0
        for next in scores:
            if next[1] > highest_score:
                highest = next
                highest_score = next[1]
        scores.remove(highest)
        sorted_scores.append(highest)
    return sorted_scores

def create_em_blank_slate(title):
    try:
        file = open(f"{title}.json", "x")
    except:
        file = open(f"{title}.json", "w")

    data = []
    to_dump = {}

    n = []
    for line in open("Names.txt", "r"):
        n.append(line.split(":"))

    for name in n:
        data.append(PlayerStats(f"{name[0]}", f"{name[1][:-1]}", [0 for i in range(20)]))

    for player in data:
        to_dump[f"{player.name}"] = {f"Name": f"{player.name}", f"Tier": f"{player.tier}", f"Data": f"{player.stats}"}
    json.dump(to_dump, file)

def load_data(filename):
    file = json.load(open(f"{filename}.json", "r"))

    data = []
    for n in _names:
        try:
            player = file[n]
            tier = player['Tier']
            name = player['Name']
            _data = player['Data'][1:-1].split(", ")

            for i, item in enumerate(_data):
                try:
                    if int(item) == float(item):
                        _data[i] = int(item)
                    else:
                        _data[i] = float(item)
                    continue
                except:
                    _data[i] = float(item)

            data.append(PlayerStats(tier, name, _data))
        except:
            print(n, "failed.")
            continue
    return data

def make_comparison(week1: int, week2: int):
    w1, w2 = load_data(f"EM-Week-{week1}"), load_data(f"EM-Week-{week2}")
    comps = []
    for player in w2:
        for play in w1:
            if player.name == play.name:
                stats = []
                for i in range(len(player.stats)):
                    stats.append(player.stats[i] - play.stats[i])
                if stats[0] == 0:
                    comps.append(PlayerStats(player.tier, player.name, [0 for i in range(20)]))
                    continue
                stats[3] = round(float(stats[1]) / float(stats[0]) * 100, 2)
                stats[10] = round(float(stats[6]) / float(stats[9]), 2)
                for i in range(5):
                    stats[10 + i] = round(float(stats[5 + i]) / float(stats[0]), 2)
                comps.append(PlayerStats(player.tier, player.name, stats))
    return comps


data = load_data("EM-Week-1")
for d in data:
    print(d)
data = make_comparison(0, 1)
for d in data:
    print(d)

