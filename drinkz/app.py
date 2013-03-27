#! /usr/bin/env python
import db, recipes, convert
from wsgiref.simple_server import make_server
import urlparse
import simplejson

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
        data = """\
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

    def error(self, environ, start_response):
        status = "404 Not Found"
        content_type = 'text/html'
        data = "Couldn't find your stuff."
       
        start_response('200 OK', list(html_headers))
        return [data]

    def inventory(self, environ, start_response):
        content_type = 'text/html'
        data = inventory()

        start_response('200 OK', list(html_headers))
        return [data]

    def liquor_types(self, environ, start_response):
        content_type = 'text/html'
        data = liquor_types()

        start_response('200 OK', list(html_headers))
        return [data]
        
    def form(self, environ, start_response):
        data = form()

        start_response('200 OK', list(html_headers))
        return [data]
   
    def recv(self, environ, start_response):
        formdata = environ['QUERY_STRING']
        results = urlparse.parse_qs(formdata)

        amount_to_convert = results['amount_to_convert'][0]
        amount_to_convert = convert.convert_to_ml(amount_to_convert)

        content_type = 'text/html'
        data = "Given amount converted to milliliters: %f. <a href='./'>Return to index.</a>" % amount_to_convert

        start_response('200 OK', list(html_headers))
        return [data]

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

    def rpc_hello(self):
        return 'world!'

    def rpc_add(self, a, b):
        return int(a) + int(b)
        
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
        
    data += "</table><p><a href='./'>Index</a> <a href='inventory'>Inventory</a> <a href='liquor_types'>Liquor Types</a> <a href='form'>Convert</a>"
    return data
    
def inventory():
    data = "<p><ul>"
    for ((m, l), a) in db._inventory_db.iteritems():
        amt = db.get_liquor_amount(m, l)
        data += "<li> " + m + l + str(amt)
    data += "</ul><p><a href='./'>Index</a> <a href='recipes'>Recipes</a> <a href='liquor_types'>Liquor Types</a> <a href='form'>Convert</a>"
    return data
    
def liquor_types():
    data = "<p><ul>"
    for (m, l, t) in db._bottle_types_db:
        data += "<li> " + m + l + t
    data += "</ul><p><a href='./'>Index</a> <a href='recipes'>Recipes</a> <a href='inventory'>Inventory</a> <a href='form'>Convert</a>"
    return data
    
def form():
    return """
<form action='recv'>
Enter amount to convert to milliliters in liters or gallons: <input type='text' name='amount_to_convert' size'20'>
<input type='submit'> <a href='./'>Return to index.</a>
</form>
"""

if __name__ == '__main__':
    import random, socket
    port = random.randint(8000, 9999)
    
    app = SimpleApp()
    
    httpd = make_server('', port, app)
    print "Serving on port %d..." % port
    print "Try using a Web browser to go to http://%s:%d/" % \
          (socket.getfqdn(), port)
    httpd.serve_forever()
