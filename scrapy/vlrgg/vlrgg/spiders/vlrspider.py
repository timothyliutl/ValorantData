import scrapy
import logging
import pandas as pd
from collections import defaultdict
from datetime import datetime

class VlrSpider(scrapy.Spider):
    name = 'valorant'
    start_urls = ['https://www.vlr.gg/event/matches/449/valorant-champions/?series_id=all', 
    'https://www.vlr.gg/event/matches/466/valorant-champions-tour-stage-3-masters-berlin/?series_id=all', 
    'https://www.vlr.gg/event/matches/353/valorant-champions-tour-stage-2-masters-reykjavik/?series_id=all&group=all']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)
    
    def parse(self, response):
        event = response.css('.wf-title::text')[0].extract().strip()
        for match in response.css('.wf-module-item.match-item.mod-color.mod-left.mod-bg-after-striped_purple'):
            link = match.attrib['href']
            yield scrapy.Request('https://www.vlr.gg' + link, callback=self.postparse, meta={'event': event})


    def postparse(self, response):
        #start scraping data for each of the maps
        #only get individual map data dont get all
        #make sure to record dates so can compare results before and after patch updates
        date = datetime.strptime(response.css('.moment-tz-convert')[0].attrib['data-utc-ts'],"%Y-%m-%d %H:%M:%S")
        winner = response.css('.wf-title-med::text')[0].extract().strip()
        loser = response.css('.wf-title-med::text')[1].extract().strip()
        mappicks = response.css('.match-header-note')
        mapdata = response.css('.vm-stats-game') #make sure to get rid of overall in list

        for map in mapdata:
            
            if not map.attrib['data-game-id']=='all':
                mapName = map.css('.map div span::text')[0].extract().strip()
                mapdf = pd.DataFrame(columns=['round', winner, loser])
                numRounds = int(response.css('.score::text').extract()[0]) + int(response.css('.score::text').extract()[1])
                counter = 1
                #parses class names to see win type for round
                for col in map.css('.vlr-rounds-row-col'):
                    if len(col.css('.rnd-sq'))==2:
                        team1_classnames = col.css('.rnd-sq')[0].xpath("@class").extract()[0]
                        team2_classnames = col.css('.rnd-sq')[1].xpath("@class").extract()[0]
                        if "win" in team1_classnames:
                            #if team1 wins
                            tempnum = 1 if 'mod-ct' in team1_classnames else 3
                            #put in here because errors with website formatting
                            if len(col.css('.rnd-sq')[0].css('img'))==0:
                                    continue
                            #if elimination win dont add anything, if objective add 1
                            if not col.css('.rnd-sq')[0].css('img')[0].attrib['src'] =='/img/vlr/game/round/elim.webp':
                                tempnum = tempnum +1
                            mapdf = mapdf.append({'round': counter, winner: tempnum, loser: 0}, ignore_index=True)
                        else:
                            if "win" in team2_classnames:
                                #if team 2 wins (losing team)
                                tempnum = 1 if 'mod-ct' in team1_classnames else 3
                                #if elimination win dont add anything, if objective add 1
                                if len(col.css('.rnd-sq')[1].css('img'))==0:
                                    continue
                                if not col.css('.rnd-sq')[1].css('img')[0].attrib['src'] =='/img/vlr/game/round/elim.webp':
                                    tempnum = tempnum + 1
                                mapdf = mapdf.append({'round': counter, winner: 0, loser: tempnum}, ignore_index= True)
                        counter = counter +1
                    mapdf.to_csv(winner + "vs" + loser + date.strftime('%d-%m-%y') + '.csv')
        yield {
            'winner':winner,
            'loser':loser,
            'numRounds': numRounds,
            'mapName': mapName,
            'event': response.meta['event']
        }

                #keys for dictionary
                #1 = ct elimination win
                #2 = ct objective win
                #3 = t elimination win
                #4 = t objective win
                #0 = loss
                #yield mapDict

