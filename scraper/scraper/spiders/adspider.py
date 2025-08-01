import scrapy
import datetime
from scraper.items import AdItem



class AdSpider(scrapy.Spider):
    name = "adspider"
    allowed_domains = ["www.pararius.nl"]
    start_urls = ["https://www.pararius.nl/huurwoningen/nederland"]

    def parse(self, response):
        country = response.css("h1.search-list-header__heading ::text").get().split()[-1]
        ad_page_links = response.css("h2.listing-search-item__title a")
        yield from response.follow_all(ad_page_links, self.parse_ad, cb_kwargs= dict(country=country))

        pagination_links = response.css("li.pagination__item.pagination__item--next a")
        yield from response.follow_all(pagination_links, self.parse)


    def parse_ad(self, response, country):
        adItem = AdItem()

        photo =  response.css("img.picture__image")
        realtor_link = response.css("h3.agent-summary__title a")

        adItem['url'] = response.url
        adItem["city"] = response.css("div.autocomplete__control input").attrib['value']
        adItem["postal_code"] = response.css("div.listing-detail-summary__location::text").get()
        adItem["country"] = country
        adItem["address"] = response.css("ol.breadcrumbs__list a::text").getall()[-1]
        adItem["rooms"] =  response.css("li.illustrated-features__item--number-of-rooms::text").get()
        adItem["surface"] =  response.css("li.illustrated-features__item--surface-area::text").get()
        adItem["price"] = response.css("div.listing-detail-summary__price span::text").get()
        adItem["website"] = response.css("header.page__wrapper.page__wrapper--masthead a::text").get()
        adItem["scraped_at"] = datetime.datetime.now().replace(microsecond=0)
        adItem["bedrooms"] = response.css("dd.listing-features__description.listing-features__description--number_of_bedrooms span::text").get()
        adItem["balcony"] = response.css("dd.listing-features__description.listing-features__description--balcony span::text").get()
        adItem["garden"] = response.css("dd.listing-features__description.listing-features__description--garden span::text").get()
        adItem["bath"] =  response.css("ul.listing-features__main-description li::text").getall()
        adItem["furnished"] = response.css("li.illustrated-features__item--interior::text").get()
        adItem["sharing"] = response.css("dd.listing-features__description--maximum_number_of_tenants span::text").get()
        adItem["pet_friendly"] = response.css("dd.listing-features__description.listing-features__description--pets_allowed span::text").get()
        adItem["income_requirement"] = response.css("dd.listing-features__description.listing-features__description--required_income span").get() is not None
        adItem["students"] = response.css("dd.listing-features__description.listing-features__description--required_statuses span::text").get()
        adItem["description"] = response.css("div.listing-detail-description__additional.listing-detail-description__additional--collapsed ::text").getall()
        adItem["photo"] = photo.attrib['src'] if photo else None
        adItem["realtor"] = response.css("h3.agent-summary__title a::text").get()
        adItem["realtor_link"] = response.urljoin(realtor_link.attrib['href']) if realtor_link else None

        yield adItem