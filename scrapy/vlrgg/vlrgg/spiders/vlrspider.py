import scrapy

class VlrSpider(scrapy.Spider):
    name = 'valorant'
    start_urls = ['https://www.vlr.gg/event/matches/449/valorant-champions/?series_id=all', 
    'https://www.vlr.gg/event/matches/466/valorant-champions-tour-stage-3-masters-berlin/?series_id=all', 
    'https://www.vlr.gg/event/matches/353/valorant-champions-tour-stage-2-masters-reykjavik']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)
    
    def parse(self, response):
        for match in response.css('.wf-module-item.match-item.mod-color.mod-left.mod-bg-after-striped_purple.mod-first'):
            link = match.attrib['href']
            yield scrapy.Request('https://www.vlr.gg' + link, callback=self.postparse)


    def postparse(self, response):
        winner = response.css('.wf-title-med::text')[0].extract().strip()
        loser = response.css('.wf-title-med::text')[1].extract().strip()
        mappicks = response.css('.match-header-note')
        yield {
            'winner': winner,
            'loser': loser,
        }