import xml.sax.handler
import string

class Player:
    def __init__(self, name, map):
        self.name = name
        self.currentCity = 0
        self.history = []
        self.map = map

    def updateHistory(self):
        if len(self.history) > 5:
            self.history.pop(0)
        self.history.append(self.map.citiesId[str(self.currentCity)])
        

    def returnHistory(self):
        string = ""
        for city in self.history:
            string += city + " > "
        return string

    def moveToCity(self, move):
        moveTmp = string.lower(move)
        if self.map.citiesName.has_key(moveTmp):
            destiny = self.map.citiesName[moveTmp]
        else:
            destiny = string.atoi(moveTmp)
        outRoads = self.map.returnRoads(self.currentCity)
        for road in outRoads:
            if road == destiny:
                self.currentCity = destiny
                self.updateHistory()
                return True
        return False
   
    def returnCityName(self):
        return self.map.returnCityName(self.currentCity)

    def isCurrentCity(self, city):
        cityTmp = string.lower(city)
        if self.map.citiesName.has_key(cityTmp):
            verify = self.map.citiesName[cityTmp]
        else:
            verify = string.atoi(cityTmp)
        if verify == self.currentCity:
            return True
        else:
            return False
    


class PlayerHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.inName = 0
        self.name = ""

    def startElement(self, name, attributes):
        self.buffer= ""
        if name == "name":
            self.inName = 1

    def characters(self, data):
        self.buffer +=data

    def endElement(self, name):
        if name == "name":
            self.inName = 0
            self.name = self.buffer
