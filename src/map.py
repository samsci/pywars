from player import Player
import xml.sax.handler
import string
from place import *
import pickle

class Map:  
    def __init__(self, citiesName, roads):
        self.placesByName = {}
        self.placesById = {}

        for city in citiesName:
            place = Place(city, citiesName[city], roads[citiesName[city]])
            self.placesByName[city] = place
            self.placesById[str(citiesName[city])] = place

    def login(self, playerName, password):
        if self.players.has_key(playerName):
            if self.players[playerName].password == password:
                player = self.players[playerName]
            else:
                player = False
        else:
            place = self.placesById["0"]
            player = Player(playerName, place.name, password)
            self.players[playerName] = player
        return pickle.dumps(player)
    
    def returnProducts(self, placeName):
        return pickle.dumps(self.placesByName[placeName].products)
    
    def returnRoads(self, placeName):
        return self.placesByName[placeName].roads

    def outCitiesString(self, placeName):
        buff = ""
        roads = self.placesByName[placeName].roads
        for road in roads:
            buff += string.capitalize(self.placesById[str(road)].name) + " "
        return buff

    def cityExists(self, placeName):
        if self.placesByName.has_key(placeName):
            return True
        else:
            return False

    
        

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

