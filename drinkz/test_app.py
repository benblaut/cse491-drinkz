#! /usr/bin/env python
import recipes, app
import sys, os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from drinkz import db
from recipes import Recipe
from wsgiref.simple_server import make_server

dispatch = {
    '/' : 'index',
    '/recipes' : 'recipes',
    '/inventory' : 'inventory',
    '/liquor_types' : 'liquor_types',
    '/form' : 'form',
    '/recv' : 'recv',
    '/rpc'  : 'dispatch_rpc'
}

html_headers = [('Content-type', 'text/html')]

def make_test_db():
    db._reset_db()

    db.add_bottle_type('Kraken', 'dark spiced rum', 'dark spiced rum')
    db.add_to_inventory('Kraken', 'dark spiced rum', '750 ml')

    db.add_bottle_type('Bols', 'blue curacao', 'citrus liqeur')
    db.add_to_inventory('Bols', 'blue curacao', '500 ml')
        
    db.add_bottle_type('Hypnotiq', 'original', 'berry liqeur')
    db.add_to_inventory('Hypnotiq', 'original', '750 ml')

    db.add_bottle_type('Uncle John\'s', 'original cider', 'apple cider')
    db.add_to_inventory('Uncle John\'s', 'original cider', '1 g')

    kraken_destroyer = Recipe('kraken destroyer', [('dark spiced rum',
                                                   '4.5 oz'), ('citrus liqeur', 
                                                   '1 oz'), ('berry liqeur', 
                                                   '1 oz'), ('apple cider', 
                                                   '8 oz')])
    db.add_recipe(kraken_destroyer)

    kraken_and_cola = Recipe('kraken and cola', [('dark spiced rum', '6 oz'),
                                            ('cola', '8 oz')])
    db.add_recipe(kraken_and_cola)

class SimpleApp(object):
    def __call__(self, environ, start_response):

        path = environ['PATH_INFO']
        fn_name = dispatch.get(path, 'error')

        # retrieve 'self.fn_name' where 'fn_name' is the
        # value in the 'dispatch' dictionary corresponding to
        # the 'path'.
        fn = getattr(self, fn_name, None)

        if fn is None:
            start_response("404 Not Found", html_headers)
            return ["No path %s found" % path]

        return fn(environ, start_response)
        
    def index(self, environ, start_response):
        data = """Index Listing<br>z
<a href='recipes'>Recipes</a>,
<a href='inventory'>Inventory</a>,
<a href='liquor_types'>Liquor Types</a>,
<a href='form'>Convert</a>
<p>
"""
        start_response('200 OK', list(html_headers))
        return [data]
        
    def recipes(self, environ, start_response):
        content_type = 'text/html'
        data = recipes()

        start_response('200 OK', list(html_headers))
        return [data]
        
def recipes():
    data = "<p><table><td><b><u>Recipe</u><b/></td><td><b><u>Have ingredients?</u></b></td><tr><td>"
    for recipe in db._recipe_db:
        need_ingredients = False
        have_ingredients_str = ""
        if recipe.need_ingredients():
            need_ingredients = True

        if need_ingredients:
            have_ingredients_str = "No"
        else:
            have_ingredients_str = "Yes"
               
        data += "<tr><td>" + recipe.name + "</td><td>" + have_ingredients_str + "</td></tr>"
        
    data += "</table><p><a href='./'>Index</a> <a href='inventory'>Inventory</a> <a href='liquor_types'>Liquor Types</a>"
    return data

def test_recipes():
    make_test_db()

    environ = {}
    environ['PATH_INFO'] = '/recipes'
    
    d = {}
    def my_start_response(s, h, return_in = d):
        d['status'] = s
        d['headers'] = h
    
    app_obj = SimpleApp()
    results = app_obj(environ, my_start_response)
    
    text = "".join(results)
    status, headers = d['status'], d['headers']
    
    assert text.find('kraken destroyer') != -1, text
    assert ('Content-type', 'text/html') in headers
    assert status == '200 OK'
