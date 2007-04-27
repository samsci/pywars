import sys
from gameexceptions import NotEnoughMoney
from player import PlayerHandler
import xml.sax
import curses
import re
import string
import xmlrpclib
import pickle

s = xmlrpclib.Server('http://localhost:8000')

STATUS_SI_Y = 20
STATUS_SI_X = 44
STATUS_OR_Y = 0
STATUS_OR_X = 0

PRODUCTS_SI_Y = 20
PRODUCTS_SI_X = 50
PRODUCTS_OR_Y = 0
PRODUCTS_OR_X = 70

INPUT_SI_Y = 5
INPUT_SI_X = 120
INPUT_OR_Y = 21
INPUT_OR_X = 0

PLAYER_SI_Y = 20
PLAYER_SI_X = 24
PLAYER_OR_Y = 0
PLAYER_OR_X = 45

STATUS_MSG_Y = 4
STATUS_MSG_X = 2

STATUS_OUT_Y = 3
STATUS_OUT_X = 2

STATUS_HISTORY_Y = 2
STATUS_HISTORY_X = 2

def printPlayer(player, playerWin):
    y = 1
    x = 1
    playerWin.addstr(y, x, string.capitalize(player.name) + " properties")
    y = y+1
    playerWin.addstr(y, x, "-"*(PLAYER_SI_X-2))
    y = y+1
    playerWin.addstr(y, x, "money = " + str(player.money))
    
def printProducts(player, productsWin):
    products = pickle.loads(s.returnProducts(player.name, player.password))
    y = 1
    x = 1
    productsWin.addstr(y, x, "Products in " + string.capitalize(player.currentPlace))
    y=y+1
    productsWin.addstr(y, x, "-"*(PRODUCTS_SI_X-2))
    y=y+1
    productsWin.addstr(y, x, "name\tquant\tvalue\t(you)\t(value)")
    y=y+1
    productsWin.addstr(y, x, "-"*(PRODUCTS_SI_X-2))
    y=y+1
    for prod in products:
        if player.products.has_key(prod):
            mine = str(player.products[prod].quantity)
            val = str(player.products[prod].value)
        else:
            mine = "n/a"
            val = "n/a"
        productsWin.addstr(y, x, prod + "\t" + str(products[prod].quantity) + "\t"
                     + str(products[prod].value) + "\t" + mine + "\t" + val)
        y=y+1

def game(screen, player):
    curses.echo()
    status = curses.newwin(STATUS_SI_Y, STATUS_SI_X, STATUS_OR_Y, STATUS_OR_X)
    input = curses.newwin(INPUT_SI_Y, INPUT_SI_X, INPUT_OR_Y, INPUT_OR_X)
    productsCli = curses.newwin(PRODUCTS_SI_Y, PRODUCTS_SI_X, PRODUCTS_OR_Y, PRODUCTS_OR_X)
    playerCli = curses.newwin(PLAYER_SI_Y, PLAYER_SI_X, PLAYER_OR_Y, PLAYER_OR_X)
    status.box()
    input.box()
    productsCli.box()
    playerCli.box()
    status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Welcome to the Game!")

    command = re.compile('(\w+)(\s(\w*))?(\s(\w*))?') 
    while 1:
        productsCli.clear()
        productsCli.box()
        printProducts(player, productsCli)
        
        playerCli.clear()
        playerCli.box()
        printPlayer(player, playerCli)
        
        input.clear()
        input.box()
        input.addstr(1, 1, ">")
        
        status.addstr(STATUS_HISTORY_Y, STATUS_HISTORY_X, "History: " + player.returnHistory())
        status.addstr(STATUS_OUT_Y, STATUS_OUT_X, "You can go to: " + s.outCitiesString(player.name, player.password))
        status.refresh()
        input.refresh()
        productsCli.refresh()
        playerCli.refresh()
        st = input.getstr(1, 3)

        cmd = command.match(st)

        if not cmd:
            continue
        status.clear()
        status.box()
        
        
        action = string.lower(cmd.group(1))
        
        ############### CURRENT ####################################
        if action == "current":
            status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "You are in "+ string.capitalize(player.currentPlace))
        
        ############### MOVE ####################################
        elif action == "move":
            destiny = cmd.group(3)
            if destiny:      
                if not s.cityExists(player.name, player.password, destiny):
                    status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "City doesn't exist!")
                elif not player.isCurrentCity(destiny):
                    placeTmp = s.moveToCity(player.name, player.password, destiny)
                    if placeTmp:
                        player.currentPlace = placeTmp
                        player.updateHistory()
                        status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Moved to " + string.capitalize(player.currentPlace))
                    else:
                        status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "There is no road to that city or you already moved this turn")
                else:
                    status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Already in " + string.capitalize(player.currentPlace))
            else:
                status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Command error: move <place>")
           
        ############### BUY ####################################
        elif action == "buy":
            amount = cmd.group(3)
            prod = cmd.group(5)
            if amount and prod:
                ver = re.compile('buy\s\d+\s\w+') 
                verify = ver.match(cmd.group(0))
                if verify:
                    try:
                        playerTmp = s.buy(player.name,player.password, prod, int(amount))
                    except xmlrpclib.Fault, e:
                        status.addstr(STATUS_MSG_Y, STATUS_MSG_X, e.faultString)
                        continue

                    if playerTmp:
                        player = pickle.loads(playerTmp)
                        status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "You now have " + str(player.products[prod].quantity) + " " + prod + "s")
                    else:
                        status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Product doesn't exist")
                else:
                    status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Command error: quantity must be a number")
            else:
                status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Command error: buy <quantity> <product>")
        ############### SELL #####################################
        elif action == "sell":
            amount = cmd.group(3)
            prod = cmd.group(5)
            if amount and prod:
                ver = re.compile('sell\s\d+\s\w+') 
                verify = ver.match(cmd.group(0))
                if verify:
                    playerTmp = s.sell(player.name, player.password, prod, int(amount))
                    
                    if playerTmp:
                        player = pickle.loads(playerTmp)
                        status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "You now have " + str(player.products[prod].quantity) + " " + prod + "s")
                    else:
                        status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Product doesn't exist")
                else:
                    status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Command error: quantity must be a number")
            else:
                status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Command error: sell <quantity> <product>")
        
        ############### TURN ################################
        elif action == "turn":
            turn = s.currentTurn(player.name, player.password)
            status.addstr(STATUS_MSG_Y, STATUS_MSG_X, str(turn[1]) + " seconds left in turn: " + str(turn[0]))
        
        ############### MYNAME ####################################
        elif action == "myname":
            status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Your name is " + string.capitalize(player.name))
       
        ############### OTHERS ####################################
        elif action == "others":
            others = s.otherPlayers(player.name, player.password)
            if len(others) == 0:
                status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Your are alone")
            else:
                out = "You are here with "
                for other in others:
                    out += other + " "
                status.addstr(STATUS_MSG_Y, STATUS_MSG_X, out)
       
        ############### HELP ####################################
        elif action == "help":
            status.addstr(STATUS_MSG_Y, STATUS_MSG_X, "Commands are: current; move <city>; myname; turn; others; exit")
        
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


