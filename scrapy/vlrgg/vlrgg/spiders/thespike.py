#code to scrape the spike data

import scrapy
import pandas as pd

class TheSpike(scrapy.Spider):
    table1 = pd.DataFrame()
    name="thespike"
    start_urls =["https://www.thespike.gg/series/valorant-champions-tour-2021/121"]

    def start_requests(self):
        yield scrapy.Request(self.start_urls[0], callback=self.pre_parse)

    def pre_parse(self, response):
        url_list = response.css('.event a')
        for link in url_list:
            yield scrapy.Request('https://www.thespike.gg/' + link.attrib['href'], callback=self.parse_event_links)
    
    def parse_event_links(self, response):
        url = response.css('.section-sub-nav-bar')[0].css('a')[1].attrib['href']
        yield scrapy.Request('https://www.thespike.gg' + url, callback=self.parse_event)
    
    def parse_event(self,response):
        for link in response.css('.single-match a'):
            url = link.attrib['href']
            yield scrapy.Request('https://www.thespike.gg' + url, callback=self.parse_match)
    
    def parse_match(self, response):
        date = response.css('.match-date::text')[0].extract().strip()
        match_data = response.css('.map-wrapper')
        del match_data[0] #remove all maps overview
        for match in match_data: #gets data for each map
            data_tables = match.css('.stat-wrap.overview-wrapper .pod.single-map')
            team1_name = match.css('.stat-wrap.overview-wrapper .team-info .team-name::text')[0].extract().strip()
            team2_name = match.css('.stat-wrap.overview-wrapper .team-info .team-name::text')[1].extract().strip()
            map_name = match.css('.map-name::text')[0].extract().strip()
            defend_first = match.css('.first-half .defending-team .team-name::text')[0].extract().strip()
            attack_first = match.css('.first-half .attacking-team .team-name::text')[0].extract().strip()
            defend_second = match.css('.second-half .defending-team .team-name::text')[0].extract().strip()
            attack_second = match.css('.second-half .attacking-team .team-name::text')[0].extract().strip()
            mappick=""
            if len(match.css('.team-pick.team-one')):
                mappick=team1_name
            if len(match.css('.team-pick.team-two')):
                mappick=team2_name
            defending_first_half_wins = match.css('.first-half .defending-team.number::text')[0].extract().strip().replace("(", '').replace(")", '')
            attacking_first_half_wins = match.css('.first-half .attacking-team.number::text')[0].extract().strip().replace("(", '').replace(")", '')
            defending_second_half_wins = match.css('.second-half .defending-team.number::text')[0].extract().strip().replace("(", '').replace(")", '')
            attacking_second_half_wins = match.css('.second-half .attacking-team.number::text')[0].extract().strip().replace("(", '').replace(")", '')
            team1_score= match.css('.team-one .team-score::text')[0].extract()
            team2_score = match.css('.team-two .team-score::text')[0].extract()
            gamekey = map_name+date+team1_name+'vs'+team2_name
            input_dict = {
                'team1_name': team1_name,
                'team2_name': team2_name,
                'map_name': map_name,
                "defending_first": defend_first,
                'attacking_first': attack_first,
                'defending_second': defend_second,
                'attacking_second': attack_second,
                'mappick':mappick,
                'defenders_first_half_wins': defending_first_half_wins,
                'attackers_first_half_wins': attacking_first_half_wins,
                'defenders_second_half_wins': defending_second_half_wins,
                'attackers_second_half_wins': attacking_second_half_wins,
                'team1_score': team1_score,
                'team2_score': team2_score,
                'winner': team1_name if team1_score>team2_score else team2_name,
                'gamekey': gamekey
            }
            self.table1 = self.table1.append(input_dict, ignore_index=True)
            yield input_dict
        self.table1.to_csv('map_overview.csv')
    #table1.to_csv('map_overview.csv')
    #will have 4 tables
    #map key - mapname+date+team1+vs+team2
    #map overview - teams, attack side won, defense side won, score at half, map pick, score at end [done]
    #player map overall stats (similar to what we had before) - kda, acs, agent of each player
    #round log - economy, first blood
    #player economy - player economy, player and gun bought at round
    #round event - time, gun used, players involved, map