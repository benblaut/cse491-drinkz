import os
from drinkz import db, recipes

try:
    os.mkdir('html')
except OSError:
    # already exists
    pass

"""
db._reset_db()

db.add_bottle_type('Johnnie Walker', 'black label', 'blended scotch')
db.add_to_inventory('Johnnie Walker', 'black label', '500 ml')
db.add_to_inventory('Johnnie Walker', 'black label', '12 oz')

db.add_bottle_type('Uncle Herman\'s', 'moonshine', 'blended scotch')
db.add_to_inventory('Uncle Herman\'s', 'moonshine', '5 liter')
        
db.add_bottle_type('Gray Goose', 'vodka', 'unflavored vodka')
db.add_to_inventory('Gray Goose', 'vodka', '1 liter')

db.add_bottle_type('Rossi', 'extra dry vermouth', 'vermouth')
db.add_to_inventory('Rossi', 'extra dry vermouth', '24 oz')

scotch_on_the_rocks = recipes.Recipe('scotch on the rocks', [('blended scotch',
                                                   '4 oz')])
db.add_recipe(scotch_on_the_rocks)

martini = recipes.Recipe('vodka martini', [('unflavored vodka', '6 oz'),
                                            ('vermouth', '1.5 oz')])
db.add_recipe(martini)

bad_martini = recipes.Recipe('vomit inducing martini', [('orange juice',
                                                      '6 oz'),
                                                     ('vermouth',
                                                      '1.5 oz')])
db.add_recipe(bad_martini)
"""

db.load_db("test_database")

###
fp = open('html/index.html', 'w')
print >> fp, "<p><a href='recipes.html'>Recipes</a>"
print >> fp, "<a href='inventory.html'>Inventory</a>"
print >> fp, "<a href='liquor_types.html'>Liquor Types</a>"

fp.close()
###

###
fp = open('html/recipes.html', 'w')
print >> fp, "<p><table>"
print >> fp, "<td><b><u>Recipe</u><b/></td><td><b><u>Have ingredients?</u></b></td>"
for recipe in db._recipe_db:
    need_ingredients = False
    have_ingredients_str = ""
    if recipe.need_ingredients():
        need_ingredients = True

    if need_ingredients:
        have_ingredients_str = "No"
    else:
        have_ingredients_str = "Yes"
    print >> fp, "<tr><td>", recipe.name, "</td>"
    print >> fp, "<td>", have_ingredients_str, "</td></tr>"
print >> fp, "</table>"
print >> fp, "<p><a href='index.html'>Index</a>"
print >> fp, "<a href='inventory.html'>Inventory</a>"
print >> fp, "<a href='liquor_types.html'>Liquor Types</a>"

fp.close()
###

###
fp = open('html/inventory.html', 'w')
print >> fp, "<p><ul>"
for ((m, l), a) in db._inventory_db.iteritems():
    amt = db.get_liquor_amount(m, l)
    print >> fp, "<li> ", m, l, amt
print >> fp, "</ul>"
print >> fp, "<p><a href='index.html'>Index</a>"
print >> fp, "<a href='recipes.html'>Recipes</a>"
print >> fp, "<a href='liquor_types.html'>Liquor Types</a>"

fp.close()
###

###
fp = open('html/liquor_types.html', 'w')
print >> fp, "<p><ul>"
for (m, l, t) in db._bottle_types_db:
    print >> fp, "<li> ", m, l, t
print >> fp, "</ul>"
print >> fp, "<p><a href='index.html'>Index</a>"
print >> fp, "<a href='recipes.html'>Recipes</a>"
print >> fp, "<a href='inventory.html'>Inventory</a>"
fp.close()
###
