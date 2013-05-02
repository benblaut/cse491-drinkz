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
import cPickle
import sqlite3
import os.path

# private singleton variables at module level
_bottle_types_db = set()
_inventory_db = {}
_recipe_db = set()

def _reset_db():
    "A method only to be used during testing -- toss the existing db info."
    global _bottle_types_db, _inventory_db, _recipe_db
    _bottle_types_db = set()
    _inventory_db = {}
    _recipe_db = set()

def save_db(filename):
    '''fp = open(filename, 'wb')

    tosave = (_bottle_types_db, _inventory_db, _recipe_db)
    dump(tosave, fp)

    fp.close()'''

    connect = sqlite3.connect(filename)

    cursor = connect.cursor()

    # clear existing tables
    cursor.execute('''drop table if exists bottle_types''')
    cursor.execute('''drop table if exists inventory''')
    cursor.execute('''drop table if exists recipes''')

    # create tables
    cursor.execute('''CREATE TABLE bottle_types (mfg text, liquor text, typ text)''')
    cursor.execute('''CREATE TABLE inventory (mfg text, liquor text, amount text)''')    
    cursor.execute('''CREATE TABLE recipes (recipe text)''')

    for entry in _bottle_types_db:
        cursor.execute("INSERT INTO bottle_types (mfg, liquor, typ) VALUES (?, ?, ?)", entry)

    for entry in _inventory_db:
        (m, l) = entry
        amt = _inventory_db[entry]
        cursor.execute("INSERT INTO inventory (mfg, liquor, amount) VALUES (?, ?, ?)", (m, l, amt))

    for entry in _recipe_db:
        serialize = cPickle.dumps(entry)

        cursor.execute("INSERT INTO recipes (recipe) VALUES (?)", [sqlite3.Binary(serialize)])

    #cursor.execute("SELECT * FROM bottle_types")
    connect.commit()
    connect.close()

def load_db(filename):
    '''global _bottle_types_db, _inventory_db, _recipe_db
    fp = open(filename, 'rb')

    loaded = load(fp)
    (_bottle_types_db, _inventory_db, _recipe_db) = loaded

    fp.close()'''

    if not os.path.isfile(filename):   
        db = sqlite3.connect(filename)
        cursor = db.cursor() 
        print "sasd"# create tables
        cursor.execute('''CREATE TABLE bottle_types (mfg text, liquor text, typ text)''')
        cursor.execute('''CREATE TABLE inventory (mfg text, liquor text, amount text)''')    
        cursor.execute('''CREATE TABLE recipes (recipe text)''')
        cursor.close()
    else:
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM bottle_types")
        results = cursor.fetchall()

        for (mfg, liquor, typ) in results:
            add_bottle_type(mfg, liquor, typ)

        cursor.execute('SELECT * FROM inventory')
        results = cursor.fetchall()
        for (mfg,liquor,amount) in results:
            add_to_inventory(mfg, liquor, amount + ' ml')
    
        for row in cursor.execute("select * from recipes"):
            add_recipe(cPickle.loads(str(row[0])))

        cursor.close()

# exceptions in Python inherit from Exception and generally don't need to
# override any methods.
class LiquorMissing(Exception):
    pass

class DuplicateRecipeName(Exception):
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
    
def get_mixable_recipes():
    "Given an inventory and list of recipes, find out which recipes can be made."
    rec_list = get_all_recipes()
    mixable_recs = []
    
    for rec in rec_list:
        if rec.is_mixable():
            mixable_recs.append(rec)
            
    return mixable_recs
