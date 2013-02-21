"""
Database functionality for drinkz information.

Recipes are stored in a set.
This is because we can already easily access the name
and ingredients of a recipe thanks to our class, and
we want to be able to search through existing recipes
quickly.
"""

import recipes

# private singleton variables at module level
_bottle_types_db = set([])
_inventory_db = dict([])
_recipe_db = set([])

def _reset_db():
    "A method only to be used during testing -- toss the existing db info."
    global _bottle_types_db, _inventory_db, _recipe_db
    _bottle_types_db = set([])
    _inventory_db = dict([])
    _recipe_db = set([])

# exceptions in Python inherit from Exception and generally don't need to
# override any methods.
class LiquorMissing(Exception):
    pass

def add_bottle_type(mfg, liquor, typ):
    "Add the given bottle type into the drinkz database."
    _bottle_types_db.add((mfg, liquor, typ))

def _check_bottle_type_exists(mfg, liquor):
    for (m, l, _) in _bottle_types_db:
        if mfg == m and liquor == l:
            return True

    return False

def add_to_inventory(mfg, liquor, amount):
    "Add the given liquor/amount to inventory."
    if not _check_bottle_type_exists(mfg, liquor):
        err = "Missing liquor: manufacturer '%s', name '%s'" % (mfg, liquor)
        raise LiquorMissing(err)

    if not check_inventory(mfg, liquor):
        # just add it to the inventory database as a tuple, for now.
        _inventory_db[(mfg, liquor)] = amount

def check_inventory(mfg, liquor):
    for ((m, l), _) in _inventory_db.iteritems():
        if mfg == m and liquor == l:
            return True
        
    return False

def check_inventory_for_type(typ):
    brands = set([])
    for (m, l, t) in _bottle_types_db:
        if t == typ:
            brands.add((m, l))

    return brands

def get_liquor_amount(mfg, liquor):
    "Retrieve the total amount of any given liquor currently in inventory."
    amounts = [] 
    found = False
    for ((m, l), amount) in _inventory_db.iteritems():
        if mfg == m and liquor == l:
            found = True
            ml_amount = convert_to_ml(amount)           
            amounts.append(ml_amount)
            total = sum(amounts)
            
            return total

    if not found:
        err = "Missing liquor: manufacturer '%s', name '%s'" % (mfg, liquor)
        raise LiquorMissing(err)

def convert_to_ml(amount):
    "Take a string of form (# unit), convert the # to ml and change unit to ml"
    amount_split = amount.split()
    float_amount = float(amount_split[0])
            
    if amount_split[1] == "ml" or amount_split[1] == "milliliter" or amount_split[1] == "milliliters":
        return float_amount
    elif amount_split[1] == "l" or amount_split[1] == "liter" or amount_split[1] == "liters":
        float_amount *= 1000
        return float_amount
    elif amount_split[1] == "oz" or amount_split[1] == "ounce" or amount_split[1] == "ounces":
        float_amount *= 29.5735
        return float_amount
    elif amount_split[1] == "gallons" or amount_split[1] == "gallon" or amount_split[1] == "g":
        float_amount *= 3785.41
        return float_amount
    else:
        print "\nIncorrect unit of measurement, use ml, g, or oz."

def get_liquor_inventory():
    "Retrieve all liquor types in inventory, in tuple form: (mfg, liquor)."
    for ((m, l), _) in _inventory_db.iteritems():
        yield m, l
        
def add_recipe(r):
    "Add a recipe r to database as a Recipe if there isn't already a recipe with the same name."
    found = False    
    for rec in _recipe_db:
        if rec.name == r.name:
            found = True

    if found == False:
        _recipe_db.add(r)
        return 1
    else:
        err = "Duplicate recipe; did not add to database."
        raise DuplicateRecipeName(err)
        return 0

class DuplicateRecipeName(Exception):
    pass
    
def get_recipe(name):
    "Retrieve the recipe object with name (name)."
    for rec in _recipe_db:
        if rec.name == name:
            return rec
        else:
            print "\nRecipe %s is not in database." % name
            return False
        
def get_all_recipes():
    "Retrieve all recipes in the database."
    recs = []
    for rec in _recipe_db:
        recs.append(rec)
        
    return recs
