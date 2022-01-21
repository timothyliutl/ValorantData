#file to get player stats for each game
import scrapy
from datetime import datetime

class PlayerDataSpider(scrapy.Spider):
    name='mappick'
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
            if len(response.css('.match-header-note::text'))!=0:
                mappicks = response.css('.match-header-note::text')[0].extract().strip()
                matchID = team1 + "vs" + team2 + date.strftime('%d-%m-%y')
                mapdata = response.css('.vm-stats-game') #make sure to get rid of overall in list
                maps = mappicks.split('; ')
                for mapname in maps:
                    data = mapname.split(' ')
                    if len(data)==3:
                        team = data[0]
                        decision = data[1]
                        name = data[2]
                        yield{
                            'team': team,
                            'decision': decision,
                            'map': name,
                            'matchID': matchID,
                            'gameID': matchID + name,
                            'date': date
                        }

