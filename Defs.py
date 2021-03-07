alphabet = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z".split(" ")
titles = "Name, Tier, Games Played, Games Won, Games Lost, Win Percentage, MVPs, Points, Goals, Assists, Saves, Shots, " \
         "Shot Percentage, Points per Game, Goals per Game, Assists per Game, Saves per Game, Shots per Game, Cycles, Hat Tricks, " \
         "Playmakers, Saviors".split(", ")
team_titles = "GM, Conference, Team, Games Played, Games Won, Games Lost, Win Percentage, Shot Percentage, Points, Goals, " \
              "Assists, Saves, Shots, Goal Difference, Opp. Shot Percentage, Opp. Points, Opp. Goals, Opp. Assists, Opp. Saves, Opp. Shots".split(", ")
tiers = "Master,Elite,Major,Minor,Challenger,Prospect,Contender,Amateur".split(",")
def get_key(key):
    lines = open("text_config.txt", "r").readlines()
    for line in lines:
        if line.startswith(key):
            return line[line.find(":") + 1:].replace("\n", "")

class PlayerStats:
    def __init__(self, tier, name, stats):
        self.tier = tier
        self.name = name
        self.games_played, self.games_won, self.game_lost, self.win_percentage, self.mvps, \
            self.points, self.goals, self.assists, self.saves, self.shots, self.shot_percentage, \
            self.ppg, self.gpg, self.apg, self.svpg, self.sopg, self.cycles, self.hat_tricks, self.playmakers,\
            self.saviors = stats
        self.stats = stats

    def __str__(self):
        return f"Tier: {self.tier}, Name: {self.name}, Stats: {self.stats}"

    def get_info(self):
        ret = [self.name, self.tier]
        for stat in self.stats:
            ret.append(stat)
        return ret

class TeamStats:
    def __init__(self, tier, stats):
        self.tier = tier
        self.gm, self.conference, self.team, self.games_played, self.games_won, self.games_lost, self.win_percentange, self.shot_percentage, self.points, self.goals, \
            self.assists, self.saves, self.shots, self.goal_difference, self.opp_shot_percentage, self.opp_points, self.opp_goals, self.opp_assists, self.opp_saves, self.opp_shots = stats
        self.name = self.team
        self.stats = stats

    def __str__(self):
        return f"Tier: {self.tier}, Name: {self.team}, Stats: {self.stats}"

    def get_info(self):
        ret = [self.team, self.tier]
        for stat in self.stats:
            ret.append(stat)
        return ret

def get_stat(info, column):
    try:
        num = info.index(column) + len(column) + 2
    except:
        return None
    ret = ""
    while True:
        if info[num] == "<":
            break
        ret += info[num]
        num += 1
    return ret

def get_stats(info):
    _stats = []
    for i in range(3, 23):
        stat = get_stat(info, f"column-{i}")
        if "%" in stat:
            stat = stat[:-1]
        try:
            _stats.append(eval(stat))
        except:
            _stats.append(0)
    return _stats

def get_team_stats(info):
    _stats = []
    for i in range(1, 21):
        stat = get_stat(info, f"column-{i}")
        if i <= 3:
            _stats.append(stat)
            continue
        if "%" in stat:
            stat = stat[:-1]
        try:
            _stats.append(eval(stat))
        except:
            _stats.append(0)
    return _stats

def differences(stat1, stat2):
    name = stat2[0]
    tier = stat2[1]
    games_played = stat2[2] - stat1[2]
    if games_played == 0:
        ret = [name, tier]
        for i in range(20):
            ret.append(0)
        return ret
    games_won = stat2[3] - stat1[3]
    games_lost = stat2[4] - stat1[4]
    win_percentage = round(games_won / games_played, 4) * 100
    mvps = stat2[6] - stat1[6]
    points = stat2[7] - stat1[7]
    goals = stat2[8] - stat1[8]
    assists = stat2[9] - stat1[9]
    saves = stat2[10] - stat1[10]
    shots = stat2[11] - stat1[11]
    cycles = stat2[18] - stat1[18]
    hat_tricks = stat2[19] - stat1[19]
    playmakers = stat2[20] - stat1[20]
    saviors = stat2[21] - stat1[21]
    return [name, tier, games_played, games_won, games_lost, win_percentage, mvps, points, goals, assists, saves, shots,
            round(goals / shots, 2), round(points / games_played, 2), round(goals / games_played, 2),
            round(assists / games_played, 2), round(saves / games_played, 2), round(shots / games_played, 2),
            cycles, hat_tricks, playmakers, saviors]
