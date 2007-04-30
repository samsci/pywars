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

lastMessages = []

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

STATUS_MSG_Y = STATUS_SI_Y + STATUS_OR_Y - 2
STATUS_MSG_X = 2

STATUS_OUT_Y = 3
STATUS_OUT_X = 2

STATUS_HISTORY_Y = 2
STATUS_HISTORY_X = 2

def processInput(message):
    return message.split()

def printMessage(message, statusWin):
    sizeOfMessages = STATUS_SI_Y - 6
    if len(lastMessages) > sizeOfMessages:
        lastMessages.pop()
    lastMessages.insert(0,message)
    y = STATUS_MSG_Y
    for message in lastMessages:
        statusWin.addstr(y, STATUS_MSG_X, message[0:STATUS_SI_X-4])
        y = y - 1

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
    printMessage("Welcome to the Game!", status)

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
        status.addstr(STATUS_OUT_Y+1, STATUS_OUT_X, "-"*(STATUS_SI_X-4))
        status.refresh()
        input.refresh()
        productsCli.refresh()
        playerCli.refresh()
        st = input.getstr(1, 3)

        cmd = processInput(st)

        if not cmd:
            continue
        status.clear()
        status.box()
        
        
        action = string.lower(cmd[0])
        args = cmd[1:]
        
        ############### CURRENT ####################################
        if action == "current":
            printMessage("You are in "+ string.capitalize(player.currentPlace), status)
        
        ############### MOVE ####################################
        elif action == "move":
            if len(args) == 1:
                destiny = args[0]
                if not s.cityExists(player.name, player.password, destiny):
                    printMessage("City doesn't exist!", status)
                elif not player.isCurrentCity(destiny):
                    placeTmp = s.moveToCity(player.name, player.password, destiny)
                    if placeTmp:
                        player.currentPlace = placeTmp
                        player.updateHistory()
                        printMessage("Moved to " + string.capitalize(player.currentPlace), status)
                    else:
                        printMessage("No road or already moved this turn", status)
                else:
                    printMessage("Already in " + string.capitalize(player.currentPlace), status)
            else:
                printMessage("Command error: move <place>", status)
           
        ############### BUY ####################################
        elif action == "buy":
            if len(args) == 2 :
                amount = args[0]
                prod = args[1]

                if args[0].isdigit():
                    try:
                        playerTmp = s.buy(player.name,player.password, prod, int(amount))
                    except xmlrpclib.Fault, e:
                        printMessage(e.faultString, status)
                        continue

                    if playerTmp:
                        player = pickle.loads(playerTmp)
                        printMessage("You now have " + str(player.products[prod].quantity) + " " + prod + "s", status)
                    else:
                        printMessage("Product doesn't exist", status)
                else:
                    printMessage("Command error: quantity must be a number", status)
            else:
                printMessage("Command error: buy <quantity> <product>", status)
        ############### SELL #####################################
        elif action == "sell":
            if len(args) == 2 :
                amount = args[0]
                prod = args[1]

                if args[0].isdigit():
                    playerTmp = s.sell(player.name, player.password, prod, int(amount))
                    
                    if playerTmp:
                        player = pickle.loads(playerTmp)
                        printMessage("You now have " + str(player.products[prod].quantity) + " " + prod + "s", status) 
                    else:
                        printMessage("Product doesn't exist", status)
                else:
                    printMessage("Command error: quantity must be a number", status)
            else:
                printMessage("Command error: sell <quantity> <product>", status)
        
        ############### SEND MESSAGE #####################################
        #elif action == "send":
        #    if len(args) >= 3:
        #        message = ""
        #        
        #    
        #    else:
        #        printMessage("Command error: send <message> to <receiver>", status)
        #
        ############### TURN ################################
        elif action == "turn":
            turn = s.currentTurn(player.name, player.password)
            printMessage(str(turn[1]) + " seconds left in turn: " + str(turn[0]), status)
        
        ############### MYNAME ####################################
        elif action == "myname":
            printMessage("Your name is " + string.capitalize(player.name), status)
       
        ############### OTHERS ####################################
        elif action == "others":
            others = s.otherPlayers(player.name, player.password)
            if len(others) == 0:
                printMessage("Your are alone", status)
            else:
                out = "You are here with "
                for other in others:
                    out += other + " "
                printMessage(out, status)
       
        ############### HELP ####################################
        elif action == "help":
            printMessage("Commands are: current; move <city>; myname; turn; others; exit", status)
        
        ############### EXIT ####################################
        elif action == "exit":
            s.logout(player.name, player.password )
            break

        ############### INVALID ####################################
        else:
            printMessage("Invalid Command", status)

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


