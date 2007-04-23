from SimpleXMLRPCServer import SimpleXMLRPCServer
import sys
import xml.sax
from map import Map, MapHandler
from products import Product, ProductsHandler
import random
    

if(len(sys.argv)<3):
    print "Usage: python pywars_server.py <xml for map> <xmf for products>"
    sys.exit(0)


mapParser = xml.sax.make_parser()
productsParser = xml.sax.make_parser()

mapHandler = MapHandler()
productsHandler = ProductsHandler()

mapParser.setContentHandler(mapHandler)
productsParser.setContentHandler(productsHandler)

mapParser.parse(sys.argv[1])
productsParser.parse(sys.argv[2])

map = Map(mapHandler.citiesName, mapHandler.roads)

for placeName in map.placesByName:
    place = map.placesByName[placeName]
    for prod in productsHandler.products:
        prodTmp = productsHandler.products[prod]
        product = Product(prod, prodTmp["value"], random.randint(int(prodTmp["min"]), int(prodTmp["max"])))
        place.products[prod] = product

del mapParser
del mapHandler
del productsParser
del productsHandler

# Create server
server = SimpleXMLRPCServer(("localhost", 8000))
server.register_introspection_functions()

# Register pow() function; this will use the value of 
# pow.__name__ as the name, which is just 'pow'.

# Register a function under a different name
#def adder_function(x,y):
#   return x + y
#server.register_function(adder_function, 'add')

# Register an instance; all the methods of the instance are 
# published as XML-RPC methods (in this case, just 'div').
#class MyFuncs:
#    def div(self, x, y): 
#        return x // y
    
server.register_instance(map)

# Run the server's main loop
server.serve_forever()