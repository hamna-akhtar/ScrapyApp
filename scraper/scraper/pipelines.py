# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re
import base64
import scrapy

def format(s):
    return s.split()[0]

class AdSpiderPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        postal_code_desc = adapter.get('postal_code')
        if postal_code_desc:
            adapter['postal_code'] = format(postal_code_desc)

        rooms_desc = adapter.get('rooms')
        if rooms_desc:
            adapter['rooms'] = format(rooms_desc)

        surface_desc = adapter.get('surface')
        if surface_desc:
            adapter['surface'] = format(surface_desc)

        price_desc= adapter.get("price")
        if price_desc:
            price = ''.join([x for x in price_desc.strip() if x.isdigit()])
            if len(price)>0:
                adapter['price'] = price
            else:
                adapter['price'] = price_desc # for 'Price on request'

        facilities = adapter.get('bath')
        if facilities:
            adapter['bath'] = False
            for facility in facilities:
                if re.search('douche', facility.lower()) or re.search('bad', facility.lower()):
                    adapter['bath'] = True

                if re.search('balkon', facility.lower()):
                    adapter['balcony'] = True
        else:
            adapter['bath'] = None

        if adapter.get('balcony') != True:
            balcony_desc = adapter.get('balcony')
            if balcony_desc:
                adapter["balcony"] = False if re.search("niet", balcony_desc.lower()) else True

        garden_desc = adapter.get('garden')
        if garden_desc:
            adapter['garden'] = format(garden_desc).lower() == "aanwezig"

        furnished_desc = adapter.get('furnished')
        if furnished_desc:
            adapter['furnished'] =  True if furnished_desc == "Gemeubileerd" else None

        num_of_tenants = adapter.get("sharing")
        if num_of_tenants:
            adapter["sharing"] = int(num_of_tenants) > 1

        pet_friendly_desc = adapter.get('pet_friendly')
        if pet_friendly_desc:
            adapter['pet_friendly'] = pet_friendly_desc.lower() == "ja"

        target_audience = adapter.get('students')
        if target_audience:
            adapter['students'] = re.search('student', target_audience.lower()) is not None

        description_string = adapter.get('description')
        if description_string:
            adapter['description'] = ''.join([x.lower() for x in description_string])

        return item


class AmsterdamSpiderPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        desc = adapter.get('description')
        if desc:
            decoded_html = base64.b64decode(desc).decode("utf-8")
            text_desc = "".join(scrapy.Selector(text=decoded_html).css("::text").getall())
            adapter['description'] = text_desc


        rooms_list = adapter.get("bedrooms")
        bedrooms = 0
        for room in rooms_list:
            if room["RuimteSoort"].lower() == "slaapkamer":
                bedrooms += 1
        adapter["bedrooms"] = bedrooms


        criterias_list = adapter.get("income_requirement")
        if criterias_list:
            adapter["income_requirement"] = False
            max_persons = 0

            for criteria in criterias_list:
                if re.search("inkomen", criteria["Label"].lower()):
                    adapter["income_requirement"] = True
                if re.search("maximum aantal personen", criteria["Label"].lower()):
                    max_persons = int(criteria["Omschrijving"])
            adapter["sharing"] = max_persons > 1
        else:
            adapter["income_requirement"] = None
            adapter["sharing"] = None


        amenity_list = adapter.get("garden")
        if amenity_list:
            adapter["garden"] = False
            adapter["balcony"] = False

            for amenity in amenity_list:
                if re.search("tuin", amenity["DetailSoort"].lower()):
                    adapter["garden"] = True
                if amenity["DetailSoort"].lower() == "balkon":
                    adapter["balcony"] = True
        else:
            adapter["garden"] = None
            adapter["balcony"] = None


        return item
