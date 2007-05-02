import xml.sax.handler


class Product:
    def __init__(self, name, value, quantity, attributes):
        self.name = name
        self.value = value
        self.quantity = quantity
        self.attributes = attributes


class ProductsHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.inName = 0
        self.inValue = 0
        self.inMax = 0
        self.inMin = 0
        self.name = ""
        self.value = ""
        self.min = ""
        self.max = ""
        self.products = {}
        self.att = None

    def startElement(self, name, attributes):
        self.buffer= ""
        if name == "name":
            self.inName = 1
        elif name == "value":
            self.inValue = 1
        elif name == "maxquantity":
            self.inMax = 1
        elif name == "minquantity":
            self.inMin = 1
        elif name == "product":
            self.att = attributes.get(u"can")

    def characters(self, data):
        self.buffer +=data

    def endElement(self, name):
        if name == "name":
            self.inName = 0
            self.name = self.buffer
        elif name == "value":
            self.inPass = 0
            self.value = self.buffer
        elif name == "maxquantity":
            self.inMax = 0
            self.max = self.buffer
        elif name == "minquantity":
            self.inMin = 0
            self.min = self.buffer
        elif name == "product":
            self.products[self.name]= {}
            self.products[self.name]["value"] = self.value
            self.products[self.name]["max"] = self.max
            self.products[self.name]["min"] = self.min
            self.products[self.name]["can"] = self.att
            self.att = None
