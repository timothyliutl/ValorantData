from datetime import datetime
import pandas as pd
data = pd.read_csv('scrapy/vlrgg/playerData/vlr.csv')
data['date'] = data['date'].apply(lambda x: datetime.strptime(x, '%d-%m-%y'))
data['playerHS'] = data['playerHS'].apply(lambda x: float(str(x).replace('%', '')))
sorted_data = data.sort_values(by=['playerName','date'])
used_cols = ['playerName','playerKills', 'playerDeaths', 'playerAssists', 'playerACS', 'playerADR', 'playerHS', 'playerFirstBlood', 'playerFirstDeath']
sorted_data[used_cols] = sorted_data.groupby('playerName')[used_cols].rolling(10).mean().reset_index().set_index('level_1')[used_cols]
sorted_data[sorted_data['playerName']=='zombs']
sorted_data.to_csv('movingAverage.csv')