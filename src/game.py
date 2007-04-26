from player import Player
import xml.sax.handler
import string
from place import *
from gameexceptions import NotEnoughMoney
import pickle
import xmlrpclib

class Game:  
    def __init__(self, name, maxPlayers, startMoney, startCity, minutesPerTurn, map):
        self.name = name
        self.maxPlayers = maxPlayers
        self.startMoney = startMoney
        self.startCity = startCity
        self.minutesPerTurn = minutesPerTurn
        self.map = map
        self.players = {}

    def validate(self, playerName, password):
        if self.players.has_key(playerName):
            if self.players[playerName].password == password:
                return True
        return False

    def login(self, playerName, password):
        if self.validate(playerName, password):
            player = self.players[playerName]
        else:
            print(self.startCity)
            place = self.map.placesById[str(self.startCity)]
            player = Player(playerName, place.name, password, int(self.startMoney))
            self.players[playerName] = player
        return pickle.dumps(player)
    
    def returnProducts(self, playerName, password):
        if not self.validate(playerName, password):
            return False
            
        placeName = self.players[playerName].currentPlace
        return self.map.returnProducts(placeName)
	    
	
    
    def returnRoads(self, playerName, password):
        if not self.validate(playerName, password):
            return False
        
        placeName = self.players[playerName].currentPlace
        return self.map.returnRoads(placeName)


    def outCitiesString(self, playerName, password):
        if not self.validate(playerName, password):
            return False
        
        placeName = self.players[playerName].currentPlace
        return self.map.outCitiesString(placeName)

    def cityExists(self,playerName, password, city):
        if not self.validate(playerName, password):
            return False
            
        return self.map.cityExists(city)
        
    def buy(self, playerName, password, productName, amount):
        if not self.validate(playerName, password):
            return False
            
        player = self.players[playerName]
        place = self.map.placesByName[player.currentPlace]
        if place.products.has_key(productName):
            product = place.products[productName]
            if product.quantity >= amount:
                bought = amount
            else:
                bought = product.quantity
           
            moneyNeeded = bought * int(product.value)
            if moneyNeeded > player.money:
                raise xmlrpclib.Fault(1,"You need " + str(moneyNeeded-player.money) + " more credits")
                
            if player.products.has_key(productName):
                player.products[productName] += bought
            else:
                player.products[productName] = bought
            product.quantity -= bought

            player.money -= moneyNeeded
            return pickle.dumps(player)
        else:
            return False
        
    def moveToCity(self, playerName, password, dest):
        if not self.validate(playerName, password):
            return False
        
        player = self.players[playerName]
        
        destTmp = string.lower(dest)
        destiny = self.map.placesByName[destTmp].id

        outRoads = self.map.placesByName[player.currentPlace].roads
        for road in outRoads:
            if road == destiny:
                place = self.map.placesById[str(destiny)]
                player.currentPlace = place.name
                player.updateHistory()
                return place.name
        return False
    
    def otherPlayers(self, playerName, password):
        if not self.validate(playerName, password):
            return False
            
        player = self.players[playerName]
        ret = []
        for key in self.players:
            other = self.players[key]
            if other.logged and other.currentPlace == player.currentPlace and other.name != playerName:
                ret.append(other)
        return ret
    
    def logout(self, playerName, password):
        if not self.validate(playerName, password):
            return False
        else:
            self.players[playerName].logged = False
            return True
    
        

class GameHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.inName = 0
        self.inMax = 0
        self.inMoney = 0
        self.inCity = 0
        self.inMinutes = 0

        self.name = ""
        self.max = ""
        self.money = ""
        self.city = ""
        self.minutes = ""
        
    def startElement(self, name, attributes):
        self.buffer = ""
        if name == "name":
            self.inName = 1
        elif name == "maxplayers":
            self.inMax = 1
        elif name == "startmoney":
            self.inMoney = 1
        elif name == "startcity":
            self.inCity = 1
        elif name == "minutesperturn":
            self.inMinutes = 1

    def characters(self, data):
        self.buffer += data

    def endElement(self, name):
        if name == "name":
            self.inName = 0
            self.name = self.buffer
        elif name == "maxplayers":
            self.inMax = 0
            self.max = int(self.buffer)
        elif name == "startmoney":
            self.inMoney = 0
            self.money = int(self.buffer)
        elif name == "startcity":
            self.inCity = 0
            self.city = int(self.buffer)
        elif name == "minutesperturn":
            self.inMinutes = 0
            self.minutes = int(self.buffer)

