import sys
from map import *
import xml.sax
import curses
import re
import string

def game(screen, map):
    curses.echo()
    status = curses.newwin(6,100,0,0)
    input = curses.newwin(5,100,7,0)
    status.border()
    input.border()
    status.addstr(3,2,"Welcome to the Game!")

    command = re.compile('(\w+)(\s(\w*))?') 
    while 1:
        input.clear()
        input.border()
        input.addstr(1,1,">")
        
        status.addstr(2,2, map.returnHistory())
        status.refresh()
        input.refresh()
        str = input.getstr(1,3)

        cmd = command.match(str)

        if not cmd:
            continue
        status.clear()
        status.border()
        
        
        action = string.lower(cmd.group(1))

        if action == "current":
            status.addstr(3,2, "You are in "+ map.returnCityName())
        elif action == "move":
            destiny = cmd.group(3)
            
            if not map.cityExists(destiny):
                status.addstr(3,2, "City doesn't exist!")
            elif not map.isCurrentCity(destiny):
                if map.moveToCity(destiny):
                    status.addstr(3,2, "Moved to " + map.returnCityName())
                else:
                    status.addstr(3,2, "There is no road to that city!")
            else:
                status.addstr(3,2, "Already in " + map.returnCityName())
        elif action == "exit":
            break
        else:
            status.addstr(3,2, "Invalid Command")

#load XML
parser = xml.sax.make_parser()
handler = MapHandler()
parser.setContentHandler(handler)
parser.parse(sys.argv[1])

map = Map(handler.citiesName, handler.citiesId, handler.roads)
del parser
del handler
#end XML

curses.wrapper(game, map)


