import xml.sax.handler
import string
from place import *
import pickle

class Map:  
    def __init__(self, citiesName, roads):
        self.placesByName = {}
        self.placesById = {}
        self.players = []

        for city in citiesName:
            place = Place(city, citiesName[city], roads[citiesName[city]])
            self.placesByName[city] = place
            self.placesById[str(citiesName[city])] = place

    def getStartPlace(self, playerName):
        self.placesById["0"].players.append(playerName)
        return pickle.dumps(self.placesById["0"])

    def returnRoads(self, city):
        return self.placesById[str(city)].roads

    def returnCityName(self, city):
        return string.capitalize(self.placesById[str(city)].name)

    def outCitiesString(self, place):
        buff = ""
        roads = self.placesById[str(place)].roads
        for road in roads:
            buff += string.capitalize(self.placesById[str(road)].name) + " "
        return buff

    def cityExists(self, city):
        cityTmp = string.lower(city)
        if self.placesByName.has_key(cityTmp):
            return True
        else:
            return False
        
    def moveToCity(self, player, origin, dest):
        destTmp = string.lower(dest)
       
        destiny = self.placesByName[destTmp].id

        outRoads = self.placesByName[origin].roads
        for road in outRoads:
            if road == destiny:
                placeOrig = self.placesByName[origin]
                placeOrig.players.remove(player)
                place = self.placesById[str(destiny)]
                place.players.append(player)
                
                return pickle.dumps(place)
        return False
    
    def otherPlayers(self, playerName, placeName):
        ret = []
        for other in self.placesByName[placeName].players:
            if(other != playerName):
                ret.append(other)
        return ret
    
    def leaveGame(self, playerName, placeName):
        self.placesByName[placeName].players.remove(playerName)
        return True

class MapHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.inName = 0
        self.inId = 0
        self.inRoute = 0
        self.id = -1
        self.routeId = -1
        self.citiesName = {}
        self.roads = {}
        
    def startElement(self, name, attributes):
        self.buffer = ""
        if name == "name":
            self.inName = 1
        elif name == "id":
            self.inId = 1
        elif name == "route":
            self.inRoute = 1

    def characters(self, data):
        self.buffer += data

    def endElement(self, name):
        if name == "name":
            self.inTitle = 0
            self.citiesName[string.lower(self.buffer)] = self.id
        elif name == "id":
            self.inId = 0
            self.id = string.atoi(self.buffer)
        elif name == "route":
            self.inRoute = 0
            if not self.roads.has_key(self.id):
                self.roads[self.id] = []
            self.roads[self.id].append(string.atoi(self.buffer))

