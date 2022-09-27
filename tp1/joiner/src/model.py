import json

from common.constants import CATEGORY_SUBFIX


class CategoryMapper:
    def __init__(self) -> None:
        self.categories = {}

    def load_category_file(self, file_name: str, file: json):
        category = json.loads(file)
        country = file_name.replace(CATEGORY_SUBFIX, '')
        self.categories[country] = {}

        for el in category['items']:
            self.categories[country][el['id']] = el['snippet']['title']

    def len(self):
        return len(self.categories)

    def map_category(self, country: str, categoryId: str) -> str:
        category_catalog = self.categories[country]
        return category_catalog[categoryId]
