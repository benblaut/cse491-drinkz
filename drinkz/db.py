"""
Database functionality for drinkz information.

Recipes are stored in a dictionary keyed by its name with its ingredients as a value.
This is because we want to be able to look up recipes efficiently by either name or ingredient list.
"""

import recipes

# private singleton variables at module level
_bottle_types_db = set([])
_inventory_db = dict([])
_recipe_db = set([])

def _reset_db():
    "A method only to be used during testing -- toss the existing db info."
    global _bottle_types_db, _inventory_db, recipes_db
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

def get_liquor_amount(mfg, liquor):
    "Retrieve the total amount of any given liquor currently in inventory."
    amounts = []     
    print _inventory_db   
    for ((m, l), amount) in _inventory_db.iteritems():
        if mfg == m and liquor == l:
            amount_split = amount.split()
            float_amount = float(amount_split[0])
            
            if amount_split[1] == "ml":
                amounts.append(float_amount)
            elif amount_split[1] == "oz":
                float_amount *= 29.5735
                amounts.append(float_amount)
            elif amount_split[1] == "gallons" or amount_split[1] == "gallon" or amount_split[1] == "g":
                float_amount *= 3785.41
                amounts.append(float_amount)
            else:
                print "\nIncorrect unit of measurement for \'%s %s %s\', use ml, g, or oz." % (m, l, amount)

            total = sum(amounts)
            #total_amount = str(total) + " ml"
            
            return total
        else:
            err = "Missing liquor: manufacturer '%s', name '%s'" % (m, l)
            raise LiquorMissing(err)

def get_liquor_inventory():
    "Retrieve all liquor types in inventory, in tuple form: (mfg, liquor)."
    for ((m, l), _) in _inventory_db.iteritems():
        yield m, l
        
def add_recipe(r):
    "Add a recipe r to database as a Recipe if there isn't already a recipe with the same name."
    
    if len(_recipe_db) == 0:
        _recipe_db.add(r)
        
    if r not in _recipe_db:
        _recipe_db.add(r)
        
    #for rec in _recipe_db:
     #   if rec.name != r.name:
      #      _recipe_db.add(r)

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
    #if (name in _recipe_db.keys()):
    #    ing = _recipe_db[name]
    #    rec = recipes.Recipe(name, ing)
    #    return rec
    #else:
        #print "\nRecipe %s not in database." % name
        #return False
        
def get_all_recipes():
    "Retrieve all recipes in the database."
    recs = []
    #for (name, ingredients) in _recipe_db.iteritems():
        #recipe = recipes.Recipe(name, ingredients)
        #recs.append(recipe)
    for rec in _recipe_db:
        recs.append(rec)
        
    return recs
