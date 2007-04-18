import sys
from map import *
from player import *
import xml.sax
import curses
import re
import string

def game(screen, player, map):
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
        
        status.addstr(2,2, player.returnHistory())
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
            status.addstr(3,2, "You are in "+ map.returnCityName(player.currentCity))
        elif action == "move":
            destiny = cmd.group(3)
            
            if not map.cityExists(destiny):
                status.addstr(3,2, "City doesn't exist!")
            elif not player.isCurrentCity(destiny):
                if player.moveToCity(destiny):
                    status.addstr(3,2, "Moved to " + player.returnCityName())
                else:
                    status.addstr(3,2, "There is no road to that city!")
            else:
                status.addstr(3,2, "Already in " + player.returnCityName())
        elif action == "exit":
            break
        else:
            status.addstr(3,2, "Invalid Command")

#load XML

if(len(sys.argv)<3):
    print "Usage: python runner.py <xml for player> <xml for map>"
    sys.exit(0)


mapParser = xml.sax.make_parser()

mapHandler = MapHandler()
mapParser.setContentHandler(mapHandler)
mapParser.parse(sys.argv[2])

map = Map(mapHandler.citiesName, mapHandler.citiesId, mapHandler.roads)
del mapParser
del mapHandler

playerParser = xml.sax.make_parser()

playerHandler = PlayerHandler()
playerParser.setContentHandler(playerHandler)
playerParser.parse(sys.argv[1])

player = Player(playerHandler.name, map)

del playerParser
del playerHandler

#end XML

curses.wrapper(game, player, map)


