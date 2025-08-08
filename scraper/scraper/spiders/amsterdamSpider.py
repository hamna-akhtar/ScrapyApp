import json
import scrapy
import datetime
from scraper.items import AdItem
from scraper.constants import Constants


class AmsterdamSpider(scrapy.Spider):
    name = "amsterdamSpider"
    allowed_domains = ["amsterdam.mijndak.nl"]
    website_name = None


    def start_requests(self):
        # for main page with all ads
        start_headers, start_payload = Constants.get_headers_payload(oftype="start")
        api_url = 'https://amsterdam.mijndak.nl/screenservices/DAKWP/Overzicht/Woningaanbod/DataActionHaalUitgelogdAanbod'
        yield scrapy.Request(
            url=api_url,
            method='POST',
            headers= start_headers,
            body=json.dumps(start_payload),
            callback=self.parse
        )

        name_headers, name_payload = Constants.get_headers_payload(oftype="name")
        name_api_url = 'https://amsterdam.mijndak.nl/screenservices/DAKWP/Common/ApplicationTitle/ScreenDataSetGetSamenwerkingsverbandsByWebsiteURL'
        yield scrapy.Request(
            url=name_api_url,
            method='POST',
            headers=name_headers,
            body=json.dumps(name_payload),
            callback=self.parse_website_name,
        )

    def parse_website_name(self, response):
        self.website_name = json.loads(response.text)["data"]["List"]["List"][0]["Samenwerkingsverband"]["DisplayNaam"]


    def parse(self, response):
        data = json.loads(response.text)["data"]
        publications = data["PublicatieLijst"]["List"]

        for item in publications:
            publication_id = item["Id"]
            photo = item["Foto_Locatie"]

            publication_headers, publication_payload = Constants.get_headers_payload("publication", publication_id)
            api_url = 'https://amsterdam.mijndak.nl/screenservices/DAKWP/HuisDetails/HuisDetails/ScreenDataSetGetPublicatie'
            yield scrapy.Request(
                url=api_url,
                method='POST',
                headers=publication_headers,
                body=json.dumps(publication_payload),
                callback=self.parse_publication,
                meta={"publication_id": publication_id, "photo": photo}
            )


    def parse_publication(self, response):
        publication_id = response.meta["publication_id"]
        data = json.loads(response.text)["data"]
        item = data["List"]["List"][0]

        address = item["Adres"]
        unit = item["Eenheid"]
        cluster = item["Cluster"]

        adItem = dict(response.meta)
        adItem['url'] = item["Publicatie"]["AdvertentieURL"]
        adItem["city"] = address["Woonplaats"]
        adItem["postal_code"] = address["Postcode"]
        adItem["address"] = f"{address["Straatnaam"]} {address["Huisnummer"]}"
        adItem["price"] = unit["NettoHuur"]
        adItem["rooms"] = unit["AantalKamers"]
        adItem["surface"] = unit["WoonVertrekkenTotOpp"]
        adItem["students"] = unit["Doelgroep"] == "Jongeren" or cluster["Doelgroep"] == "Jongeren"
        adItem["senior_home"] = unit["Doelgroep"] == 'Senioren' or cluster["Doelgroep"] == "Senioren"
        adItem["scraped_at"] = datetime.datetime.now().replace(microsecond=0)

        detail_headers, detail_payload = Constants.get_headers_payload("detail", publication_id)
        detail_api_url = 'https://amsterdam.mijndak.nl/screenservices/DAKWP/HuisDetails/HuisDetails_WB/DataActionGetPublicatieDetails'
        yield scrapy.Request(
            url=detail_api_url,
            method='POST',
            headers=detail_headers,
            body=json.dumps(detail_payload),
            callback=self.parse_publication_detail,
            meta=adItem
        )


    def parse_publication_detail(self, response):
        adItem = AdItem()
        data = json.loads(response.text)["data"]

        adItem["income_requirement"] = data["SelectieCriteriaList"]["List"]
        adItem["bedrooms"] = data["VertrekkenList"]["List"]
        adItem["garden"] = data["VoorzieningList"]['List']
        adItem["description"] = data["PublicatieTekst"]["Tekst"]

        adItem['url'] = response.meta['url']
        adItem["city"] = response.meta['city']
        adItem["postal_code"] = response.meta['postal_code']
        adItem["address"] = response.meta['address']
        adItem["price"] = response.meta['price']
        adItem["rooms"] = response.meta['rooms']
        adItem["surface"] = response.meta['surface']
        adItem["students"] = response.meta['students']
        adItem["senior_home"] = response.meta['senior_home']
        adItem["scraped_at"] = response.meta['scraped_at']
        adItem["photo"] = response.meta["photo"]
        adItem["website"] = self.website_name

        yield adItem