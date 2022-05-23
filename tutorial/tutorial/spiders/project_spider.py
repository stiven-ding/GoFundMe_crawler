import os
from time import sleep
from unittest import case
import scrapy
import json
from furl import furl
from datetime import date
import dateparser
from tutorial.items import *


class ProjectSpider(scrapy.Spider):
    name = "project_spider"

    custom_settings = {
        'AUTOTHROTTLE_ENABLED': False,
        'AUTOTHROTTLE_START_DELAY': 0.2,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 0.7,
        'LOG_LEVEL': 'INFO'
    }

    def api_builder(self, project_id, call, page=0):
        if(call == 'counts'):
            url = 'https://gateway.gofundme.com/web-gateway/v1/feed/' + project_id + '/counts'
        elif(call == 'comments'):
            url = 'https://gateway.gofundme.com/web-gateway/v1/feed/' + \
                project_id + '/comments?limit=20&offset=' + str(page * 20)
        elif(call == 'highest_donations'):
            url = 'https://gateway.gofundme.com/web-gateway/v1/feed/' + \
                project_id + '/donations?limit=20&offset=' + \
                str(page * 20) + '&sort=highest'
        elif(call == 'donations'):
            url = 'https://gateway.gofundme.com/web-gateway/v1/feed/' + \
                project_id + '/donations?limit=20&offset=' + \
                str(page * 20) + '&sort=recent'
        elif(call == 'updates'):
            url = 'https://gateway.gofundme.com/web-gateway/v1/feed/' + \
                project_id + '/updates?limit=20&offset=' + str(page * 20)
        elif(call == 'velocity'):
            url = 'https://gateway.gofundme.com/web-gateway/v1/feed/' + \
                project_id + '/velocity?type=recent_donations'
        elif(call == 'photos'):
            url = 'https://gateway.gofundme.com/web-gateway/v1/feed/' + \
                project_id + '/photos?limit=20&offset=0&photo_type=4'
        else:
            scrapy.exceptions.DropItem("Missing data")
        return url

    def start_requests(self):
        url_db_file = open('./url/url_db.json', 'r')
        url_db_json = json.load(url_db_file)

        for item in url_db_json:
            yield scrapy.Request(url=item['url'], callback=self.parse, meta={
                'id': item['id'],
                'catagory': item['catagory'],
                'location': item['location'],
                'date_url_discovered': item['date_url_discovered']
            })

    def parse(self, response):
        project = ProjectItem()

        project['id'] = response.meta['id']
        project['url'] = response.url
        project['title'] = response.css("h1::text").get()
        project['date_created_friendly'] = response.css(
            "span.a-created-date::text").get().replace('Created ', '')
        project['date_created_parsed'] = dateparser.parse(
            project['date_created_friendly']).isoformat()
        project['image'] = response.css(
            'div.a-image--background::attr(style)').re(r"background-image:url\((.*)\)")[0]
        project['catagory'] = response.meta['catagory']
        project['location'] = response.meta['location']
        project['percentage_funded'] = response.css(
            "progress.a-progress-bar::attr(value)").get()

        # new project without any doantions
        if response.css("h2.m-progress-meter-heading::text").get() is None:
            project['amount_goal'] = response.css("h2.m-progress-meter-heading--exp").css("div::text").get().replace(
                ' raised of ', '').replace(' goal', '').replace(',', '')
            project['amount_raised'] = "0"
        
        # old project with donations
        else:
            project['amount_goal'] = response.css("span.text-stat::text").get().replace(
                ' raised of ', '').replace(' goal', '').replace(',', '')
            project['amount_raised'] = response.css(
                "h2.m-progress-meter-heading::text").get().replace(',', '')

        project['description'] = response.css(
            "div.o-campaign-description").get()
        project['date_url_discovered'] = response.meta['date_url_discovered']

        project['comments'] = []
        project['updates'] = []
        project['photos'] = []
        project['highest_donations'] = []
        project['donations'] = []
        project['organizers'] = []
        project['beneficiaries'] = []

        status = {
            'counts': False,
            'velocity': False,
            'comments': False,
            'updates': False,
            'photos': False,
            'donations': False
        }

        yield scrapy.Request(url=self.api_builder(project['id'], 'counts'),
                             callback=self.parse_counts,
                             meta={'project': project, 'status': status})

    def parse_counts(self, response):
        project = response.meta['project']
        status = response.meta['status']

        references = json.loads(response.text)["references"]
        project['counts'] = references['counts']

        response.meta['status']['counts'] = True
        yield scrapy.Request(url=self.api_builder(project['id'], 'velocity'),
                             callback=self.parse_velocity,
                             meta={'project': project, 'status': status})

    def parse_velocity(self, response):
        project = response.meta['project']
        status = response.meta['status']

        references = json.loads(response.text)["references"]
        project['velocity'] = references['velocity']['recent_donations']

        response.meta['status']['velocity'] = True
        yield scrapy.Request(self.api_builder(project['id'], 'comments'),
                             callback=self.parse_comments,
                             meta={'project': project, 'status': status, 'page': 0})

    def parse_comments(self, response):
        project = response.meta['project']
        status = response.meta['status']
        page = response.meta['page']

        references = json.loads(response.text)["references"]
        meta = json.loads(response.text)['meta']

        contents = references['contents'] if 'contents' in references else []

        for content in contents:
            comment = content['comment']

            if 'donation' in content:
                comment['name'] = content['donation']['name']
                comment['amount_donation'] = content['donation']['amount']
            else:
                comment['amount_donation'] = content['amount'] if 'amount' in content else 0

            project["comments"].append(comment)

        if('has_next' in meta and meta['has_next'] == True and page < 10):
            yield scrapy.Request(url=self.api_builder(project['id'], 'comments', page + 1),
                                 callback=self.parse_comments,
                                 meta={'project': project, 'status': status, 'page': page + 1})
        else:
            response.meta['status']['comments'] = True
            yield scrapy.Request(self.api_builder(project['id'], 'updates'),
                                 callback=self.parse_updates,
                                 meta={'project': project, 'status': status, 'page': 0})

    def parse_updates(self, response):
        project = response.meta['project']
        status = response.meta['status']
        page = response.meta['page']

        references = json.loads(response.text)["references"]
        meta = json.loads(response.text)['meta']

        updates = references['updates'] if 'updates' in references else []

        for update in updates:
            project["updates"].append(update)

        if('has_next' in meta and meta['has_next'] == True and page < 10):
            yield scrapy.Request(url=self.api_builder(project['id'], 'updates', page + 1),
                                 callback=self.parse_updates,
                                 meta={'project': project, 'status': status, 'page': page + 1})
        else:
            response.meta['status']['updates'] = True
            yield scrapy.Request(self.api_builder(project['id'], 'photos'),
                                 callback=self.parse_photos,
                                 meta={'project': project, 'status': status, 'page': 0})

    def parse_photos(self, response):
        project = response.meta['project']
        status = response.meta['status']
        page = response.meta['page']

        references = json.loads(response.text)["references"]
        meta = json.loads(response.text)['meta']

        photos = references['photos'] if 'photos' in references else []

        for photo in photos:
            project["photos"].append(photo)

        if('has_next' in meta and meta['has_next'] == True and page < 10):
            yield scrapy.Request(url=self.api_builder(project['id'], 'photos', page + 1),
                                 callback=self.parse_photos,
                                 meta={'project': project, 'status': status, 'page': page + 1})
        else:
            response.meta['status']['photos'] = True
            yield scrapy.Request(self.api_builder(project['id'], 'highest_donations'),
                                 callback=self.parse_highest_donations,
                                 meta={'project': project, 'status': status})

    def parse_highest_donations(self, response):
        project = response.meta['project']
        status = response.meta['status']

        references = json.loads(response.text)["references"]

        donations = references['donations'] if 'donations' in references else []
        for donation in donations:
            project["highest_donations"].append(donation)

        response.meta['status']['highest_donations'] = True
        yield scrapy.Request(self.api_builder(project['id'], 'donations'),
                             callback=self.parse_donations,
                             meta={'project': project, 'status': status, 'page': 0})

    def parse_donations(self, response):
        project = response.meta['project']
        status = response.meta['status']
        page = response.meta['page']

        references = json.loads(response.text)["references"]
        meta = json.loads(response.text)['meta']

        donations = references['donations'] if 'donations' in references else []

        for donation in donations:
            project["donations"].append(donation)

        if('has_next' in meta and meta['has_next'] == True and page < 10):
            yield scrapy.Request(url=self.api_builder(project['id'], 'donations', page + 1),
                                 callback=self.parse_donations,
                                 meta={'project': project, 'status': status, 'page': page + 1})
        else:
            response.meta['status']['donations'] = True
            yield scrapy.Request(project['url'],
                                 callback=self.parse_organizers,
                                 meta={'project': project, 'status': status}, dont_filter=True)

    def parse_organizers(self, response):
        project = response.meta['project']
        status = response.meta['status']

        # organizer
        for element in response.css("div.m-campaign-members-main-organizer, div.m-campaign-members-team"):
            organizer = OrganizerItem()
            # If organization, name is in a span tag.
            if element.css("div.m-organization-info"):
                organizer['name'] = element.css("span::text").get()
            # if individual, name is in a div tag.
            if element.css("div.m-person-info-name"):
                organizer['name'] = element.css(
                    "div.m-person-info-name::text").get()
            organizer['content'] = element.css(
                "div.text-small").css("div::text").getall()
            project['organizers'].append(organizer)

        # beneficiary
        for element in response.css("div.m-campaign-members-main-beneficiary"):
            organizer = OrganizerItem()
            # If organization, name is in a span tag.
            if element.css("div.m-organization-info"):
                organizer['name'] = element.css("span::text").get()
            # if individual, name is in a div tag.
            if element.css("div.m-person-info-name"):
                organizer['name'] = element.css(
                    "div.m-person-info-name::text").get()
            organizer['content'] = element.css(
                "div.text-small").css("div::text").getall()
            project['beneficiaries'].append(organizer)

        all_parsed = True
        for s in status:
            if s == False:
                all_parsed = False
                break
        if all_parsed:
            yield project
        else:
            raise scrapy.exceptions.DropItem("Missing data")
