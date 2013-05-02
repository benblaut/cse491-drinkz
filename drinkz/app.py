#! /usr/bin/env python
import recipes, convert
import urlparse
import simplejson
import jinja2
import uuid
import sys, os.path

from wsgiref.simple_server import make_server
from Cookie import SimpleCookie

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from drinkz import db

loader = jinja2.FileSystemLoader('./templates')
env = jinja2.Environment(loader=loader)

dispatch = {
    '/' : 'login',
    '/login_start' : 'login',
    '/login_execute' : 'login_execute',
    '/logout' : 'logout',
    '/status' : 'status',
    '/index' : 'index',
    '/post' : 'post',
    '/image' : 'image',
    '/recipes' : 'recipes',
    '/recipes_add' : 'recipes_add',
    '/inventory' : 'inventory',
    '/inventory_add' : 'inventory_add',
    '/liquor_types' : 'liquor_types',
    '/liquor_types_add' : 'liquor_types_add',
    '/convert_form' : 'convert_form',
    '/do_convert' : 'do_convert',
    '/rpc'  : 'dispatch_rpc'
}

html_headers = [('Content-type', 'text/html')]

db.load_db("database.db")

usernames = {}

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

    def error(self, environ, start_response):
        status = "404 Not Found"
        content_type = 'text/html'
        data = "Couldn't find your stuff."
       
        start_response('200 OK', list(html_headers))
        return [data]

    def post(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            data = 'Post operation successful.'
        else:
            data = 'Post operation unsuccessful.'

        start_response('200 OK', list(html_headers))
        return [data]

    def image(self, environ, start_response):
        content_type = 'image/gif'
        data = open('../Spartan.gif', 'rb').read()

        start_response('200 OK', [('Content-type', content_type)])
        return [data]
            
    def index(self, environ, start_response):
        name = ''
        name_key = '*empty*'
        if 'HTTP_COOKIE' in environ:
            c = SimpleCookie(environ.get('HTTP_COOKIE', ''))
            if 'name' in c:
                key = c.get('name').value
                name = usernames.get(key, '')
                name_key = key
        if name == '':
            return self.login(environ, start_response)

        start_response('200 OK', list(html_headers))

        template = env.get_template("index.html")

        title = "index"
        return str(template.render(locals()))

    def login(self, environ, start_response):
        name = ''
        name_key = '*empty*'
        if 'HTTP_COOKIE' in environ:
            c = SimpleCookie(environ.get('HTTP_COOKIE', ''))
            if 'name' in c:
                key = c.get('name').value
                name = usernames.get(key, '')
                name_key = key
        if name:
            return self.index(environ, start_response)
        else:
            start_response('200 OK', list(html_headers))
            title = 'login'
            template = env.get_template("login.html")
            return str(template.render(locals()))

    def login_execute(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        name = results['name'][0]
        content_type = 'text/html'

        # authentication would go here -- is this a valid username/password,
        # for example?

        k = str(uuid.uuid4())
        usernames[k] = name

        headers = list(html_headers)
        headers.append(('Location', '/index'))
        headers.append(('Set-Cookie', 'name=%s' % k))

        start_response('302 Found', headers)
        return ["Redirect to /index..."]

    def logout(self, environ, start_response):
        if 'HTTP_COOKIE' in environ:
            c = SimpleCookie(environ.get('HTTP_COOKIE', ''))
            if 'name' in c:
                key = c.get('name').value
                name_key = key

                if key in usernames:
                    del usernames[key]
                    print 'DELETING'

        pair = ('Set-Cookie',
                'name=deleted; Expires=Thu, 01-Jan-1970 00:00:01 GMT;')
        headers = list(html_headers)
        headers.append(('Location', '/status'))
        headers.append(pair)

        start_response('302 Found', headers)
        return ["Redirect to /status..."]

    def status(self, environ, start_response):
        start_response('200 OK', list(html_headers))

        name = ''
        name_key = '*empty*'
        if 'HTTP_COOKIE' in environ:
            c = SimpleCookie(environ.get('HTTP_COOKIE', ''))
            if 'name' in c:
                key = c.get('name').value
                name = usernames.get(key, '')
                name_key = key
                
        title = 'login status'
        template = env.get_template('status.html')
        return str(template.render(locals()))
        
    def recipes(self, environ, start_response):
        start_response('200 OK', list(html_headers))

        title = "recipes"
        recipes = [r for r in db.get_all_recipes()]

        template = env.get_template("recipes.html")
        return str(template.render(locals()))

    def recipes_add(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        name = results['name'][0]
        ingredients = results['ingredients'][0]

        ingredients = ingredients.splitlines()
        ingredients = [ x.strip() for x in ingredients ] # clean whitespace
        ingredients = [ x for x in ingredients if x ]    # remove empty
        ingredients = [ x.split(',') for x in ingredients ]

        r = recipes.Recipe(name, ingredients)
        db.add_recipe(r)
        db.save_db("database.db")
        
        headers = list(html_headers)
        headers.append(('Location', '/recipes'))

        start_response('302 Found', headers)
        return ["Redirect to /recipes..."]

    def inventory(self, environ, start_response):
        start_response('200 OK', list(html_headers))
        
        title = "inventory"
        inventory = [(m, l, db.get_liquor_amount(m, l)) \
                      for (m, l) in db.get_liquor_inventory()]

        template = env.get_template("inventory.html")
        return str(template.render(locals()))

    def inventory_add(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        mfg = results['mfg'][0]
        liquor = results['liquor'][0]
        amount = results['amount'][0]
        db.add_to_inventory(mfg, liquor, amount)
        db.save_db("database.db")
        
        headers = list(html_headers)
        headers.append(('Location', '/inventory'))

        start_response('302 Found', headers)
        return ["Redirect to /inventory..."]

    def liquor_types(self, environ, start_response):
        start_response("200 OK", list(html_headers))

        title = "liquor types"

        liquor_types = [(m, l, t) for (m, l, t) in db._bottle_types_db]
        
        template = env.get_template("liquor_types.html")
        return str(template.render(locals()))

    def liquor_types_add(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        mfg = results['mfg'][0]
        liquor = results['liquor'][0]
        typ = results['typ'][0]
        db.add_bottle_type(mfg, liquor, typ)
        db.save_db("database.db")
        
        headers = list(html_headers)
        headers.append(('Location', '/liquor_types'))

        start_response('302 Found', headers)
        return ["Redirect to /liquor_types..."]
        
    def convert_form(self, environ, start_response):
        start_response("200 OK", list(html_headers))
        title = "convert form"
        template = env.get_template("convert_form.html")
        return str(template.render(locals()))

    def do_convert(self, environ, start_response):
        start_response("200 OK", list(html_headers))

        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)
        
        amount = results['amount'][0]
        amount = convert.convert_to_ml(amount)

        x = ["Amount is: %s ml" % (amount,)]
        return x

    def dispatch_rpc(self, environ, start_response):
        # POST requests deliver input data via a file-like handle,
        # with the size of the data specified by CONTENT_LENGTH;
        # see the WSGI PEP.
        
        if environ['REQUEST_METHOD'].endswith('POST'):
            body = None
            if environ.get('CONTENT_LENGTH'):
                length = int(environ['CONTENT_LENGTH'])
                body = environ['wsgi.input'].read(length)
                response = self._dispatch(body) + '\n'
                start_response('200 OK', [('Content-Type', 'application/json')])

                return [response]

        # default to a non JSON-RPC error.
        status = "404 Not Found"
        content_type = 'text/html'
        data = "Couldn't find your stuff."
       
        start_response('200 OK', list(html_headers))
        return [data]

    def _decode(self, json):
        return simplejson.loads(json)

    def _dispatch(self, json):
        rpc_request = self._decode(json)

        method = rpc_request['method']
        params = rpc_request['params']
        
        rpc_fn_name = 'rpc_' + method
        fn = getattr(self, rpc_fn_name)
        result = fn(*params)

        response = { 'result' : result, 'error' : None, 'id' : 1 }
        response = simplejson.dumps(response)
        return str(response)

    def rpc_convert_units_to_ml(self, amount):
        return convert.convert_to_ml(amount)

    def rpc_get_recipe_names(self):
        all_recipes = db.get_all_recipes()
        recipe_names = []
        for rec in all_recipes:
            recipe_names.append(rec.name)

        return recipe_names

    def rpc_get_liquor_inventory(self):
        inventory = []
        pairing = ()
        for (mfg, liquor) in db.get_liquor_inventory():
            pairing = (mfg, liquor)
            inventory.append(pairing)
        return inventory

    def rpc_add_recipe(self, name, ingredients):
        r = recipes.Recipe(name, ingredients)
        db.add_recipe(r)

    def rpc_add_bottle_type(self, mfg, liquor, typ):
        db.add_bottle_type(mfg, liquor, typ)

    def rpc_add_to_inventory(self, mfg, liquor, amount):
        db.add_to_inventory(mfg, liquor, amount)

if __name__ == '__main__':
    import random, socket
    port = random.randint(8000, 9999)
    port = 8766
    app = SimpleApp()
    
    httpd = make_server('', port, app)
    print "Serving on port %d..." % port
    print "Try using a Web browser to go to http://%s:%d/" % \
          (socket.getfqdn(), port)
    httpd.serve_forever()
