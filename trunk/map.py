import xml.sax.handler
import string

class Map:
    def __init__(self, citiesName, citiesId, roads):
        self.citiesName = citiesName
        self.citiesId = citiesId
        self.roads = roads
        

    def returnRoads(self, city):
        return self.roads[city]

    def returnCityName(self, city):
        return self.citiesId[str(city)]

    def cityExists(self, city):
        cityTmp = string.lower(city)
        if self.citiesName.has_key(cityTmp):
            return True
        elif self.citiesId.has_key(cityTmp):
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
        self.citiesId = {}
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
            self.citiesId[str(self.id)] = string.lower(self.buffer)
        elif name == "id":
            self.inId = 0
            self.id = string.atoi(self.buffer)
        elif name == "route":
            self.inRoute = 0
            if not self.roads.has_key(self.id):
                self.roads[self.id] = []
            self.roads[self.id].append(string.atoi(self.buffer))

