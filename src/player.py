import xml.sax.handler
import string

class Player:
    def __init__(self, name, currentPlace, password, money):
        self.name = name
        self.money = money
        self.currentPlace = currentPlace
        self.history = [string.capitalize(self.currentPlace)]
        self.password = password
        self.logged = True
        self.products = {}
        self.turn = 0

    def updateHistory(self):
        if len(self.history) > 2:
            self.history.pop(0)
        self.history.append(string.capitalize(self.currentPlace))
        

    def returnHistory(self):
        string = ""
        for city in self.history:
            string += city + " > "
        return string

   
    def returnCityName(self):
        return self.currentPlace

    def isCurrentCity(self, city):
        cityTmp = string.lower(city)
        if self.currentPlace == cityTmp:
            return True
        else:
            return False
    


class PlayerHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.inName = 0
        self.inPass = 0
        self.name = ""
        self.password = ""

    def startElement(self, name, attributes):
        self.buffer= ""
        if name == "name":
            self.inName = 1
        elif name == "password":
            self.inPass = 1

    def characters(self, data):
        self.buffer +=data

    def endElement(self, name):
        if name == "name":
            self.inName = 0
            self.name = self.buffer
        if name == "password":
            self.inPass = 0
            self.password = self.buffer
