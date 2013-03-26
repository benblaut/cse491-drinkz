"""
Database functionality for drinkz information.

Recipes are stored in a set.
This is because we can already easily access the name
and ingredients of a recipe thanks to our class, and
we want to be able to search through existing recipes
quickly.
"""

import recipes
import convert

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
    else:
        amount_to_add = convert.convert_to_ml(amount)
        old_amount = get_liquor_amount(mfg, liquor)
        new_amount = amount_to_add + old_amount
        amount_str = str(new_amount) + " ml"
        _inventory_db[(mfg, liquor)] = amount_str

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
            ml_amount = convert.convert_to_ml(amount)           
            amounts.append(ml_amount)
            total = sum(amounts)
            
            return total

    if not found:
        err = "Missing liquor: manufacturer '%s', name '%s'" % (mfg, liquor)
        raise LiquorMissing(err)

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
