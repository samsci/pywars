import xml.sax.handler
import string

class Player:
    def __init__(self, name, currentPlace):
        self.name = name
        self.currentPlace = currentPlace
        self.history = [string.capitalize(self.currentPlace.name)]

    def updateHistory(self):
        if len(self.history) > 5:
            self.history.pop(0)
        self.history.append(string.capitalize(self.currentPlace.name))
        

    def returnHistory(self):
        string = ""
        for city in self.history:
            string += city + " > "
        return string

   
    def returnCityName(self):
        return self.currentPlace.name

    def isCurrentCity(self, city):
        cityTmp = string.lower(city)
        if self.currentPlace.name == cityTmp or str(self.currentPlace.id) == cityTmp:
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
