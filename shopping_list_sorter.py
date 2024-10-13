from store_layout import store_layout
from category_keywords import category_keywords
from fuzzywuzzy import process
import unicodedata

class ShoppingListSorter:
    def __init__(self):
        self.store_layout = store_layout
        self.category_keywords = category_keywords
        self.all_keywords = [self.remove_diacritics(keyword) for keywords in self.category_keywords.values() for keyword in keywords]

    def remove_diacritics(self, text):
        return ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c)).lower()

    def guess_category(self, item):
        item = self.remove_diacritics(item)

        # Exact match
        for category, keywords in self.category_keywords.items():
            if item in [self.remove_diacritics(keyword) for keyword in keywords]:
                return category

        # Fuzzy match
        best_match = process.extractOne(item, self.all_keywords, score_cutoff=80)
        if best_match:
            matched_keyword = best_match[0]
            for category, keywords in self.category_keywords.items():
                if matched_keyword in [self.remove_diacritics(keyword) for keyword in keywords]:
                    return category

        return 'ostatní'

    def sort_shopping_list(self, shopping_list):
        def get_aisle_number(item):
            category = self.guess_category(item)
            return next((aisle for aisle, section in self.store_layout.items() if section == category), float('inf'))

        sorted_list = sorted(shopping_list, key=get_aisle_number)
        return sorted_list