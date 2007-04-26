from SimpleXMLRPCServer import SimpleXMLRPCServer
import sys
import xml.sax
from map import Map, MapHandler
from products import Product, ProductsHandler
from game import Game, GameHandler
import random
    

if(len(sys.argv)<4):
    print "Usage: python pywars_server.py <xml for game> <xml for map> <xmf for products>"
    sys.exit(0)


mapParser = xml.sax.make_parser()
productsParser = xml.sax.make_parser()
gameParser = xml.sax.make_parser()

mapHandler = MapHandler()
productsHandler = ProductsHandler()
gameHandler = GameHandler()

mapParser.setContentHandler(mapHandler)
productsParser.setContentHandler(productsHandler)
gameParser.setContentHandler(gameHandler)

gameParser.parse(sys.argv[1])
mapParser.parse(sys.argv[2])
productsParser.parse(sys.argv[3])

map = Map(mapHandler.citiesName, mapHandler.roads)

for placeName in map.placesByName:
    place = map.placesByName[placeName]
    for prod in productsHandler.products:
        prodTmp = productsHandler.products[prod]
        product = Product(prod, prodTmp["value"], random.randint(int(prodTmp["min"]), int(prodTmp["max"])))
        place.products[prod] = product
        
game = Game(gameHandler.name, gameHandler.max, gameHandler.money, gameHandler.city, gameHandler.minutes, map)

del mapParser
del mapHandler
del productsParser
del productsHandler
del gameParser
del gameHandler

# Create server
server = SimpleXMLRPCServer(("localhost", 8000))
server.register_introspection_functions()


    
server.register_instance(game)

# Run the server's main loop
server.serve_forever()
