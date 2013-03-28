#! /usr/bin/env python
import sys, os.path
import simplejson
import urllib2
import app, recipes
import StringIO
import collections

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from drinkz import db
from recipes import Recipe

def call_remote(method, params, id):
    d = dict(method = method, params = params, id = id)

    environ = {}
    environ['PATH_INFO'] = '/rpc'
    environ['REQUEST_METHOD'] = 'POST'
    environ['CONTENT_LENGTH'] = len(simplejson.dumps(d))
    environ['wsgi.input'] = StringIO.StringIO(simplejson.dumps(d))


    d={}

    def my_start_response(s, h, return_in = d):
        d['status'] = s
        d['headers'] = h

    app_obj = app.SimpleApp()
    results = app_obj(environ, my_start_response)

    status, headers = d['status'], d['headers']

    result = "".join(results)

    assert ('Content-Type', 'application/json') in headers
    assert status == '200 OK'

    return result

def test_json_convert_units_to_ml():
    conversion = call_remote('convert_units_to_ml', ["1 gallon"], '1')

    rpc_request = simplejson.loads(conversion)

    result = rpc_request['result']

    assert result == 3785.41, result

def test_json_get_recipe_names():
    make_test_db()

    names = call_remote('get_recipe_names', [], '1')

    rpc_request = simplejson.loads(names)

    result = rpc_request['result']

    correct_result = ['kraken destroyer', 'kraken and cola']

    assert collections.Counter(result) == collections.Counter(correct_result), result

def test_json_get_liquor_inventory():
    make_test_db()

    inventory = call_remote('get_liquor_inventory', [], 1)

    rpc_request = simplejson.loads(inventory)

    result = rpc_request['result']

    assert ['Kraken', 'dark spiced rum'] in result, result
    assert ['Bols', 'blue curacao'] in result, result
    assert ['Hypnotiq', 'original'] in result, result
    assert ['Uncle John\'s', 'original cider'] in result, result

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

