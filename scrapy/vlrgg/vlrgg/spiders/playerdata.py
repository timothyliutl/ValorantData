#file to get player stats for each game
import scrapy
from datetime import datetime

class PlayerDataSpider(scrapy.Spider):
    name='PlayerData'
    start_urls = ['https://www.vlr.gg/vct-2021']
    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self.pre_parse)

    def pre_parse(self, response):
        url_list = response.css('.event-item')
        for url in url_list:
            yield scrapy.Request('https://www.vlr.gg'+url.attrib['href'], callback=self.parse_event_links)

    def parse_event_links(self,response):
            match_urls = response.css('.wf-nav-item')[1]
            all_url = 'https://www.vlr.gg'+match_urls.attrib['href']
            yield scrapy.Request(all_url.split('=')[0]+'=all&group=all', callback=self.parse)
       
    def parse(self, response):
        event = response.css('.wf-title::text')[0].extract().strip()
        for match in response.css('.wf-module-item.match-item.mod-color.mod-left'):
            link = match.attrib['href']
            yield scrapy.Request('https://www.vlr.gg' + link, callback=self.postparse, meta={'event': event})
    def postparse(self, response):
            date = datetime.strptime(response.css('.moment-tz-convert')[0].attrib['data-utc-ts'],"%Y-%m-%d %H:%M:%S")
            team1 = response.css('.vlr-rounds-row-col')[0].css('.team::text')[1].extract().strip().upper()
            team2 = response.css('.vlr-rounds-row-col')[0].css('.team::text')[3].extract().strip().upper()
            mappicks = response.css('.match-header-note')
            mapdata = response.css('.vm-stats-game') #make sure to get rid of overall in list

            for map in mapdata:
                #could add event for future use
                if not map.attrib['data-game-id']=='all':
                    mapName = map.css('.map div span::text')[0].extract().strip()
                    winnerCTWins = int(map.css('.mod-ct::text')[0].extract().strip())
                    loserCTWins = int(map.css('.mod-ct::text')[1].extract().strip())
                    winnerTWins = int(map.css('.mod-t::text')[0].extract().strip())
                    loserTWins = int(map.css('.mod-t::text')[1].extract().strip())
                    team1Result = int(map.css('.score::text')[0].extract().strip())
                    team2Result = int(map.css('.score::text')[1].extract().strip())
                    winner = team1 if team1Result>team2Result else team2
                    playerData = map.css('tbody tr')
                    for player in playerData:
                        playerName = player.css('.mod-player a div::text')[0].extract().strip()
                        playerTeam = player.css('.mod-player a div::text')[1].extract().strip().upper()
                        playerKills = player.css('.mod-vlr-kills span::text')[0].extract().strip()
                        playerDeaths = player.css('.mod-vlr-deaths span span::text')[1].extract().strip()
                        playerAssists = player.css('.mod-vlr-assists span::text')[0].extract().strip()
                        playerADR = player.css('.stats-sq.mod-combat::text')[0].extract().strip()
                        playerACS = player.css('.stats-sq::text')[0].extract().strip()
                        playerHS = player.css('.stats-sq::text')[6].extract().strip()
                        playerFirstBlood = player.css('.mod-stat.mod-fb span::text')[0].extract().strip()
                        playerFirstDeath = player.css('.mod-stat.mod-fd span::text')[0].extract().strip()
                        matchID = team1 + "vs" + team2 + date.strftime('%d-%m-%y')
                        opponent = team2 if team1.upper()==playerTeam.upper() else team1
                        result = 'Win' if playerTeam.upper()==winner.upper() else 'Lose'
                        playerAgent = player.css('.stats-sq.mod-agent img')[0].attrib['title']
                        yield{
                            'playerName': playerName,
                            'playerTeam': playerTeam,
                            'map': mapName,
                            'playerAgent': playerAgent,
                            'playerKills': playerKills,
                            'playerDeaths': playerDeaths,
                            'playerAssists':playerAssists,
                            'playerACS':playerACS,
                            'playerADR':playerADR,
                            'playerHS':playerHS,
                            'playerFirstBlood':playerFirstBlood,
                            'playerFirstDeath':playerFirstDeath,
                            'matchID':matchID,
                            'opponent': opponent,
                            'result': result,
                            'winnerRoundsWon':team1Result if team1Result>team2Result else team2Result,
                            'loserRoundsWon':team2Result if team1Result>team2Result else team1Result,
                            'winningTeam': winner,
                            'date': date.strftime('%d-%m-%y'),
                            'event': response.meta['event']
                        }

