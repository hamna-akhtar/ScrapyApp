# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re

def format(s):
    return s.split()[0]

class AdScraperPipeline:
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
