import sys
sys.path.insert(0, 'bin/')

from cStringIO import StringIO
import imp

import db, load_bulk_data
import recipes

def start_load_bottle_types(path, print_output):
    db._reset_db()
    
    test_data_path = path
    fp = open(test_data_path, 'r')
    try:
        n = load_bulk_data.load_bottle_types(fp)
    except ValueError:
        print "\nIncorrect string format for \'load_bulk_data.load_bottle_types\' in \'%s\'." % test_data_path
        print "Correct usage: \'manufacturer name,liquor name,liquor type\'\n"
        pass
    
    if print_output:
        print "\n%s" % db._bottle_types_db
    
def start_load_inventory(path):
    db._reset_db()
    
    start_load_bottle_types('test-data/bottle-types-data-1.txt', False)
    
    test_data_path = path
    fp = open(test_data_path, 'r')
    try:
        n = load_bulk_data.load_inventory(fp)
    except db.LiquorMissing:
        print "\nCould not find liquor: Incorrect string for \'load_bulk_data.load_inventory\' in \'%s\'." % test_data_path
        print "Correct usage: \'manufacturer name,liquor name,amount ml\'\n"
        pass
    except ValueError:
        print "\nIncorrect string format for \'load_bulk_data.load_inventory\' in \'%s\'." % test_data_path
        print "Correct usage: \'manufacturer name,liquor name,liquor type\'\n"
        pass
        
    print "\n%s" % db._inventory_db
    
def test_load_bottle_types_1():
    start_load_bottle_types('test-data/bottle-types-data-1.txt', True)

def test_load_bottle_types_2():
    start_load_bottle_types('test-data/bottle-types-data-2.txt', True)

def test_load_inventory_1():
    start_load_inventory('test-data/inventory-data-1.txt')

def test_load_inventory_2():
    start_load_inventory('test-data/inventory-data-2.txt')

def test_get_liquor_amount_1():
    db._reset_db()

    db.add_bottle_type('Johnnie Walker', 'Black Label', 'blended scotch')
    db.add_to_inventory('Johnnie Walker', 'Black Label', '1000 ml')
    db.add_to_inventory('Johnnie Walker', 'Black Label', '750 ml')
    db.add_to_inventory('Johnnie Walker', 'Black Label', '250 ml')
    amount = db.get_liquor_amount('Johnnie Walker', 'Black Label')

    print "\n%s" % amount

def test_get_liquor_amount_2():
    db._reset_db()

    db.add_bottle_type('Johnnie Walker', 'Black Label', 'blended scotch')
    db.add_to_inventory('Johnnie Walker', 'Black Label', '1000 ml')
    db.add_to_inventory('Johnnie Walker', 'Black Label', '325 oz')
    db.add_to_inventory('Johnnie Walker', 'Black Label', '1 g')
    amount = db.get_liquor_amount('Johnnie Walker', 'Black Label')

    print "\n%s" % amount

def test_get_liquor_amount_3():
    db._reset_db()

    db.add_bottle_type('Johnnie Walker', 'Black Label', 'blended scotch')
    db.add_to_inventory('Johnnie Walker', 'Black Label', '1000 ml')
    db.add_to_inventory('Johnnie Walker', 'Black Label', '750 g')
    db.add_to_inventory('Johnnie Walker', 'Black Label', '250 ml')
    amount = db.get_liquor_amount('Johnnie Walker', 'Black Label')

    print "\n%s" % amount

def script_load_bottle_types():
    scriptpath = 'bin/load-liquor-types'
    module = imp.load_source('llt', scriptpath)
    exit_code = module.main([scriptpath, 'test-data/bottle-types-data-1.txt'])


def test_script_load_inventory():
    script_load_bottle_types()

    scriptpath = 'bin/load-liquor-inventory'
    module = imp.load_source('lli', scriptpath)
    exit_code = module.main([scriptpath, 'test-data/inventory-data-1.txt'])
    
def test_create_recipe():
    r = recipes.Recipe('vodka martini', [('vodka', '6 oz'), ('vermouth', '1 oz')])

    assert r.name == 'vodka martini'
    assert r.ingredients == [('vodka', '6 oz'), ('vermouth', '1 oz')]
    print r.name, r.ingredients
    
def test_add_recipe():
    db._reset_db()
    r = recipes.Recipe('vodka martini', [('vodka', '6 oz'), ('vermouth', '1 oz')])
    db.add_recipe(r)

    assert len(db._recipe_db) == 1
    print db._recipe_db
    
def test_get_recipe():
    db._reset_db()
    r = recipes.Recipe('vodka martini', [('vodka', '6 oz'), ('vermouth', '1 oz')])
    db.add_recipe(r)
    x = db.get_recipe('vodka martini')
    
    assert r == x
    if(x):
        print x.name, x.ingredients

def test_get_all_recipes():
    db._reset_db()
    r = recipes.Recipe('vodka martini', [('vodka', '6 oz'), ('vermouth', '1 oz')])
    db.add_recipe(r)
    r2 = recipes.Recipe('screwdriver', [('orange juice', '6 oz'), ('vodka', '1 oz')])
    db.add_recipe(r2)
    x = db.get_all_recipes()

    assert len(x) == 2
    for rec in x:
        print rec.name, rec.ingredients

def test_convert_to_ml():
    data = ["1 ml", "1 milliliter", "2 milliliters", "2 l", "1 l", "10 l", "10 oz", "1 ounce", "15 ounces", "2 g", "1 gallon", "5 gallons"]
    converted_data = []

    for entry in data:
        converted = db.convert_to_ml(entry)
        converted_data.append(converted)

    assert converted_data == [1.0, 1.0, 2.0, 2000.0, 1000.0, 10000.0, 295.735, 29.5735, 443.60249999999996, 7570.82, 3785.41, 18927.05]
    print converted_data
    
test_create_recipe()
print ""
test_add_recipe()
print ""
test_get_recipe()
print ""
test_get_all_recipes()
print ""
test_convert_to_ml()
print ""


test_load_bottle_types_1()
test_load_bottle_types_2()
test_load_inventory_1()
test_load_inventory_2()
test_get_liquor_amount_1()
test_get_liquor_amount_2()
test_get_liquor_amount_3()

print ""

test_script_load_inventory()

print ""
