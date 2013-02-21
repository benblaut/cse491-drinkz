import db

class Recipe(object):
    def __init__(self, name = '', ingredients = [()]):
        self.name = name
        self.ingredients = ingredients

    def need_ingredients(self):
        types_needed = []
        ingredients_needed = []
        for (typ, amt) in self.ingredients:
            amt = db.convert_to_ml(amt)
            brands_owned = db.check_inventory_for_type(typ)
            if len(brands_owned) == 0:
                types_needed.append((typ, amt))
            else:
                amounts_from_brands = []
                for (m, l) in brands_owned:
                    amount_owned_of_brand = db.get_liquor_amount(m, l)
                    amounts_from_brands.append(amount_owned_of_brand)
                if (amount_owned_of_brand <= amt):
                    amount_needed = amt - amount_owned_of_brand
                    ingredients_needed.append((typ, amount_needed))
        
        for (type_needed, amount_needed) in types_needed:
            ingredients_needed.append((type_needed, amount_needed))

        return ingredients_needed
