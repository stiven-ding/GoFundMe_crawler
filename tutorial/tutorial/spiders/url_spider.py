import scrapy
from furl import furl
from datetime import date


class UrlSpider(scrapy.Spider):
    name = "url_spider"

    custom_settings = {
        'LOG_LEVEL': 'INFO'
    }
    def start_requests(self):
        catagories = {"emergency": 2, "animals": 3, "family": 4, "business": 5, "event": 6, "community": 7,
                      "creative": 8, "memorial": 9, "travel": 10, "medical": 11, "faith": 12, "non_profit": 13,
                      "miscellaneous": 15, "sports": 16, "volunteer": 18, "competition": 19, "wishes": 20,
                      "financial_emergency": 344, "environment": 342}

        for cname in catagories:
            cid = catagories[cname]
            for page in range(1, 10):
                url = "https://www.gofundme.com/mvc.php?route=categorypages/load_more&page=" + str(page) + "&term=&cid=" + str(cid) 
                yield scrapy.Request(url=url, callback=self.parse, meta={'catagory': cname})

    def parse(self, response):
        cname = response.meta['catagory']

        for item in response.css('div.grid-item'):
            yield {
                'id': item.css("a::attr(aria-labelledby)").get(),
                'url': item.css("a::attr(href)").get(),
                'title': item.css("div.fund-title.show-for-medium::text").get(), 
                'image': item.css("div.campaign-tile-img--contain::attr(data-original)").get(),
                'catagory': cname,
                'location': item.css("div.fund-location").css("span::text").get(),
                'date_url_discovered': date.today().strftime("%Y-%m-%d"),
            }

 