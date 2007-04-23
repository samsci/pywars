import sys
from player import PlayerHandler
import xml.sax
import curses
import re
import string
import xmlrpclib
import pickle

s = xmlrpclib.Server('http://localhost:8000')

STATUS_SI_Y = 7
STATUS_SI_X = 100
STATUS_OR_Y = 0
STATUS_OR_X = 0

INPUT_SI_Y = 5
INPUT_SI_X = 100
INPUT_OR_Y = 8
INPUT_OR_X = 0

STATUS_MSG_Y = 4
STATUS_MSG_X = 2

STATUS_OUT_Y = 3
STATUS_OUT_X = 2

STATUS_HISTORY_Y = 2
STATUS_HISTORY_X = 2


def game(screen, player):
    curses.echo()
    status = curses.newwin(STATUS_SI_Y, STATUS_SI_X, STATUS_OR_Y, STATUS_OR_X)
    input = curses.newwin(INPUT_SI_Y, INPUT_SI_X, INPUT_OR_Y, INPUT_OR_X)
    status.border()
    input.border()
    status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Welcome to the Game!")

    command = re.compile('(\w+)(\s(\w*))?') 
    while 1:
        input.clear()
        input.border()
        input.addstr(1, 1, ">")
        
        status.addstr(STATUS_HISTORY_Y, STATUS_HISTORY_X, "History: " + player.returnHistory())
        status.addstr(STATUS_OUT_Y, STATUS_OUT_X, "You can go to: " + s.outCitiesString(player.currentPlace.id))
        status.refresh()
        input.refresh()
        st = input.getstr(1, 3)

        cmd = command.match(st)

        if not cmd:
            continue
        status.clear()
        status.border()
        
        
        action = string.lower(cmd.group(1))
        
        ############### CURRENT ####################################
        if action == "current":
            status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "You are in "+ string.capitalize(player.currentPlace.name))
        
        ############### MOVE ####################################
        elif action == "move":
            destiny = cmd.group(3)
            
            if not s.cityExists(destiny):
                status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "City doesn't exist!")
            elif not player.isCurrentCity(destiny):
                placeTmp = s.moveToCity(player.name, player.currentPlace.name, destiny)
                if placeTmp:
                    placeTmp = pickle.loads(placeTmp)
                    player.currentPlace = placeTmp
                    player.updateHistory()
                    status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Moved to " + string.capitalize(player.returnCityName()))
                else:
                    status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "There is no road to that city!")
            else:
                status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Already in " + string.capitalize(player.returnCityName()))
       
        ############### MYNAME ####################################
        elif action == "myname":
            status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Your name is " + string.capitalize(player.name))
       
        ############### OTHERS ####################################
        elif action == "others":
            others = s.otherPlayers(player.name, player.currentPlace.name)
            if len(others) == 0:
                status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Your are alone")
            else:
                out = "You are here with "
                for other in others:
                    out += other + " "
                status.addstr(STATUS_MSG_Y, STATUS_MSG_X, out)
       
        ############### HELP ####################################
        elif action == "help":
            status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Commands are: current; move <city>; myname; others; exit")
        
        ############### EXIT ####################################
        elif action == "exit":
            s.logout(player.name, player.password )
            break

        ############### INVALID ####################################
        else:
            status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Invalid Command")

#load XML

if(len(sys.argv)<2):
    print "Usage: python pywars.py <xml for player>"
    sys.exit(0)

playerParser = xml.sax.make_parser()

playerHandler = PlayerHandler()
playerParser.setContentHandler(playerHandler)
playerParser.parse(sys.argv[1])

tryLogin = s.login(playerHandler.name, playerHandler.password)
if tryLogin:
    player = pickle.loads(tryLogin)
else:
    print "Login failed: Wrong password"
    sys.exit(0)

del playerParser
del playerHandler

#end XML

curses.wrapper(game, player)


