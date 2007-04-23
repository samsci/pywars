from SimpleXMLRPCServer import SimpleXMLRPCServer
import sys
from map import Map, MapHandler
import xml.sax
    

if(len(sys.argv)<2):
    print "Usage: python pywars_server.py <xml for map>"
    sys.exit(0)


mapParser = xml.sax.make_parser()

mapHandler = MapHandler()
mapParser.setContentHandler(mapHandler)
mapParser.parse(sys.argv[1])

map = Map(mapHandler.citiesName, mapHandler.roads)


del mapParser
del mapHandler


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