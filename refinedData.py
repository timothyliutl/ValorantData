#resorting data so that it is indexed by game
#can skip this step with csv file
import pandas as pd
data = pd.read_csv('scrapy/vlrgg/playerData/vlr.csv')
refined_data = pd.DataFrame()

for match in data['matchID'].unique():
    map_names = data[data['matchID']==match]['map'].unique()
    for map_name in map_names:
        match_data = data[(data['matchID']==match)&(data['map']==map_name)]
        if len(match_data.index)!=10:
            #disregard incomplete games or games with less than 10 players
            print('Error: skipping incomplete match data')
            continue
        teams = match_data['playerTeam'].unique()
        try:
            team1players = match_data[match_data['playerTeam']==teams[0]]['playerName'].unique()
            team2players = match_data[match_data['playerTeam']==teams[1]]['playerName'].unique()
        except:
            print("Error: empty teams")
        try:
            refined_data =  refined_data.append(
                {'player1':team1players[0],
                'player2':team1players[1],
                'player3':team1players[2],
                'player4':team1players[3],
                'player5':team1players[4],
                'team': teams[0],
                'o_team': teams[1],
                'o_player1':team2players[0],
                'o_player2':team2players[1],
                'o_player3':team2players[2],
                'o_player4':team2players[3],
                'o_player5':team2players[4],
                'player1_agent':match_data[match_data['playerName']==team1players[0]]['playerAgent'].values[0],
                'player2_agent':match_data[match_data['playerName']==team1players[1]]['playerAgent'].values[0],
                'player3_agent':match_data[match_data['playerName']==team1players[2]]['playerAgent'].values[0],
                'player4_agent':match_data[match_data['playerName']==team1players[3]]['playerAgent'].values[0],
                'player5_agent':match_data[match_data['playerName']==team1players[4]]['playerAgent'].values[0],
                'o_player1_agent':match_data[match_data['playerName']==team2players[0]]['playerAgent'].values[0],
                'o_player2_agent':match_data[match_data['playerName']==team2players[1]]['playerAgent'].values[0],
                'o_player3_agent':match_data[match_data['playerName']==team2players[2]]['playerAgent'].values[0],
                'o_player4_agent':match_data[match_data['playerName']==team2players[3]]['playerAgent'].values[0],
                'o_player5_agent':match_data[match_data['playerName']==team2players[4]]['playerAgent'].values[0],
                'map': map_name,
                'result': match_data[match_data['playerName']==team1players[0]]['result'].values[0],
                'date': match_data[match_data['playerName']==team1players[0]]['date'].values[0]
                }, ignore_index=True)
        except:
            print("Error: skipping weird data")
refined_data.to_csv('refined.csv')

