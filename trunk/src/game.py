from player import Player
import xml.sax.handler
import string
from place import *
from products import *
from gameexceptions import NotEnoughMoney
import pickle
import xmlrpclib
import time
import random

class Game:  
    def __init__(self, name, maxPlayers, startMoney, startCity, secondsPerTurn, map):
        self.name = name
        self.maxPlayers = maxPlayers
        self.startMoney = startMoney
        self.startCity = startCity
        self.secondsPerTurn = secondsPerTurn
        self.map = map
        self.players = {}
        self.turn = 0
        self.lastTime = time.time()
        self.playersMoved = []
        
    def reevaluate(self):
        places = self.map.placesByName
        for placeName in places:
            place = places[placeName]
            for productName in place.products:
                product = place.products[productName]
                newVal = int(product.value * (0.01 *random.randint(-10, 10)) + product.value)
                if newVal > 0:
                    product.value = newVal
            
    def processMove(self, playerName):
        if playerName in self.playersMoved:
            return False
        else:
            self.playersMoved.append(playerName)
            return True
        
    def processTurn(self):
        now = time.time()
        diff = self.lastTime + self.secondsPerTurn
        if diff < now:
            self.lastTime = now
            self.turn += 1
            self.playersMoved = []
            self.reevaluate()
            print("Turn changed: "+ str(self.turn))
            
    def currentTurn(self, playerName, password):
        if not self.validate(playerName, password):
            return False
        diff = self.lastTime + self.secondsPerTurn - time.time()
        return [self.turn, int(diff)]
            
    def validate(self, playerName, password):
        if self.players.has_key(playerName):
            if self.players[playerName].password == password:
                return True
        return False

    def login(self, playerName, password):
        if self.validate(playerName, password):
            player = self.players[playerName]
        else:
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
                if amount == 0 and product.quantity != 0:
                    bought = int(player.money / product.value)
                else:
                    bought = amount
            else:
                bought = product.quantity
           
            moneyNeeded = bought * int(product.value)
            if moneyNeeded > player.money:
                raise xmlrpclib.Fault(1,"You need " + str(moneyNeeded-player.money) + " more credits")
                
            if player.products.has_key(productName):
                player.products[productName].quantity += bought
            else:
                player.products[productName] = Product(productName, product.value, bought)
            product.quantity -= bought

            player.money -= moneyNeeded
            return pickle.dumps(player)
        else:
            return False
    
    def sell(self, playerName, password, productName, amount):
        if not self.validate(playerName, password):
            return False
        
        player = self.players[playerName]
        place = self.map.placesByName[player.currentPlace]
        
        if place.products.has_key(productName) and player.products.has_key(productName):
            placeProduct = place.products[productName]
            if amount <= player.products[productName].quantity:
                sold = amount
            else:
                sold = player.products[productName].quantity
                
            player.products[productName].quantity -= sold
            player.money += sold * int(placeProduct.value)
            placeProduct.quantity += sold
            return pickle.dumps(player)
        else:
            return False
    
    def moveToCity(self, playerName, password, dest):
        if not self.validate(playerName, password):
            return False
            
        if not self.processMove(playerName):
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
        self.inSeconds = 0

        self.name = ""
        self.max = ""
        self.money = ""
        self.city = ""
        self.seconds = ""
        
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
        elif name == "secondsperturn":
            self.inSeconds = 1

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
        elif name == "secondsperturn":
            self.inSeconds = 0
            self.seconds = int(self.buffer)

