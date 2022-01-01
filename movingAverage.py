from datetime import datetime
import pandas as pd
imported_data = pd.read_csv('scrapy/vlrgg/playerData/vlr.csv').dropna()
data = pd.DataFrame()
for match in imported_data['matchID'].unique():
    map_names = imported_data[imported_data['matchID']==match]['map'].unique()
    for map_name in map_names:
        match_data = imported_data[(imported_data['matchID']==match)&(imported_data['map']==map_name)]
        if len(match_data.index)!=10:
            print('Error: skipping incomplete matches')
            continue
        else:
            data = data.append(match_data)
#checking for incomplete data
data.to_csv('cleanedData.csv')


data['date'] = data['date'].apply(lambda x: datetime.strptime(x, '%d-%m-%y'))
data['playerHS'] = data['playerHS'].apply(lambda x: float(str(x).replace('%', '')))
sorted_data = data.sort_values(by=['playerName','date'])
used_cols = ['playerName','playerKills', 'playerDeaths', 'playerAssists', 'playerACS', 'playerADR', 'playerHS', 'playerFirstBlood', 'playerFirstDeath']
sorted_data[used_cols] = sorted_data[used_cols].shift(1)
sorted_data[used_cols] = sorted_data.groupby('playerName')[used_cols].rolling(10).mean().reset_index().set_index('level_1')[used_cols]
sorted_data[sorted_data['playerName']=='zombs']
sorted_data.to_csv('movingAverage2.csv')