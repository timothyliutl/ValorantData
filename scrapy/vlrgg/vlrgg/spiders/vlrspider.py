import scrapy
import logging
import pandas as pd
from collections import defaultdict
from datetime import datetime
#use playerdata for more correct data
#first iteration of scraper
#will update this once vlr adds game logs to site

class VlrSpider(scrapy.Spider):
    name = 'valorant'
    start_urls = ['https://www.vlr.gg/vct-2021']
    #update this so we dont have to get these links ourselves
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
                mapdf = pd.DataFrame(columns=['round', 'winningTeamRound', 'losingTeamRound', 'date', 'map', 'event', 'winner', 'loser', 'matchid'])
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
                            mapdf = mapdf.append({'round': counter, 'winningTeamRound': tempnum, 'losingTeamRound': 0,'date': date.strftime('%d-%m-%y'), 'map': mapName, 'event': response.meta['event'], 'winner':winner, 'loser':loser, 'matchid':winner + "vs" + loser + date.strftime('%d-%m-%y')}, ignore_index=True)
                        else:
                            if "win" in team2_classnames:
                                #if team 2 wins (losing team)
                                tempnum = 1 if 'mod-ct' in team1_classnames else 3
                                #if elimination win dont add anything, if objective add 1
                                if len(col.css('.rnd-sq')[1].css('img'))==0:
                                    continue
                                if not col.css('.rnd-sq')[1].css('img')[0].attrib['src'] =='/img/vlr/game/round/elim.webp':
                                    tempnum = tempnum + 1
                                mapdf = mapdf.append({'round': counter, 'winningTeamRound': 0, 'losingTeamRound': tempnum, 'date': date.strftime('%d-%m-%y'), 'map': mapName, 'event': response.meta['event'], 'winner':winner, 'loser':loser, 
                                'matchid': winner + "vs" + loser + date.strftime('%d-%m-%y')}, ignore_index= True)
                        counter = counter +1
        mapdf.to_csv('rounds.csv')
        yield {
            'winner':winner,
            'loser':loser,
            'numRounds': numRounds,
            'mapName': mapName,
            'event': response.meta['event'],
            'date':date
        }

                #keys for dictionary
                #1 = ct elimination win
                #2 = ct objective win
                #3 = t elimination win
                #4 = t objective win
                #0 = loss
                #yield mapDict

