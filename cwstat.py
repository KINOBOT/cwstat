import requests
import json
import curses
import os, sys


#GLOBAL VARIABLES
KEY_ESCAPE = 27
KEY_ZERO = 48
KEY_A = 65
KEY_L = 76
KEY_Q = 81
KEY_R = 82
KEY_S = 83
KEY_C = 67
KEY_a = 97
KEY_l = 108
KEY_q = 113
KEY_r = 114
KEY_s = 115
KEY_c = 99
KEY_LEFT = 260
KEY_RIGHT = 261
KEY_ENTER = 10

COINDATA = {}

FIELD_LENGTH = 20
BUTTONS = [ '[A] Add/Modify Coin ', '[R] Remove Coin ', '[L] List all Coins ', '[C] Cycle Sorting ', '[Q] Quit ']

USAGE = '[<>] to navigate [ENTER] to select'

BASEDIR = os.path.join(os.path.expanduser('~'), '.cwstat')
WALLETFILE = os.path.join(BASEDIR, 'wallet.json')


ASCIIART1 = '   __ _______  ______  ___  ____ ______                      __       __       '
ASCIIART2 = '  / //_/  _/ |/ / __ \/ _ )/ __ /_  __/ ____  _____    _____/ /____ _/ /_  ____'
ASCIIART3 = ' / .< _/ //    / /_/ / _  / /_/ // /   /___/ / __| |/|/ (_-/ __/ _ `/ __/ /___/'
ASCIIART4 = '/_/|_/___/_/|_/\____/____/\____//_/          \__/|__/__/___\__/\___/\__/       '
 

class Coin:
    def __init__(self):
        self.data = ''

    def __init__(self, jsondata ):
        self.data = jsondata

    def Symbol(self):
        return self.data['symbol']
    
    def Name(self):
        return self.data['name']

    def Usd(self):
        return self.data['price_usd']
    
    def Change1h(self):
        return self.data['percent_change_1h']  

    def Change24h(self):
        return self.data['percent_change_24h']   
    

def UpdateCoindata():
    url = 'https://api.coinmarketcap.com/v1/ticker/'

    try:
        r = requests.get(url)
    except requests.exceptions.RequestException:
        sys.exit('Could not get live ticker')

    try:
        jdata = r.json()
        COINDATA.clear()
        for entry in jdata:
            c = Coin( entry )
            COINDATA[c.Symbol()] = c
    except:
        sys.exit('Could not parse data')

def WriteWallet():
    with open(WALLETFILE, 'w') as f:
        json.dump(WALLET, f)

def ReadWallet():
    try:
        with open(WALLETFILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def ReadStringFromCmd(stdscr, prompt):
    curses.echo()
    stdscr.clear()
    stdscr.addnstr(0, 0, prompt, -1, curses.color_pair(2))
    curses.curs_set(1)
    stdscr.refresh()
    inputStr = stdscr.getstr(1, 0, 20).decode()
    curses.noecho()
    curses.curs_set(0)
    stdscr.clear()
    curses.halfdelay(10)
    return inputStr

def DrawMenu(stdscr, y, x):
    allButtons = ''.join( BUTTONS )
    sel = BUTTONS[CURRENTMENU]

    selStart = 0
    
    for i in range( CURRENTMENU ):
        selStart += len(BUTTONS[i])
    
    selEnd = selStart + len(sel)

    beforeSel = ''
    if CURRENTMENU > 0:
        beforeSel = allButtons[0:selStart]
    
    afterSel = allButtons[selEnd:-1]

    stdscr.addnstr( y-2,0, beforeSel, x, curses.color_pair(2) )
    stdscr.addnstr( y-2,len(beforeSel), sel, x, curses.color_pair(5) )
    stdscr.addnstr( y-2,len(beforeSel)+len(sel), afterSel, x, curses.color_pair(2) )
    stdscr.addnstr( y-1, 0, USAGE, x, curses.color_pair(2) )


def Draw(stdscr, y, x ):
    spacer_for_4 = ' ' * (FIELD_LENGTH - 4)
    spacer_for_5 = ' ' * (FIELD_LENGTH - 5)
    spacer_for_7 = ' ' * (FIELD_LENGTH - 7)
    spacer_for_9 = ' ' * (FIELD_LENGTH - 9)
    spacer_for_10 = ' ' * (FIELD_LENGTH - 10)

    global DRAWLIST
    global SORTING

    if DRAWLIST:
        stdscr.clear()
        
        stdscr.addnstr( 0, 0, "AVAILABLE COINS", x, curses.color_pair(4) )
        stdscr.addnstr( y - 1, 0, "[L] to go back", x, curses.color_pair(2) )

        allCoins = list(COINDATA.keys())
        allCoins.sort()
        numCoins = len(allCoins)

        for i in range(numCoins):
            coinSymbol = allCoins[i]
            coinSymbolLong = coinSymbol + (' ' * (5 - len(coinSymbol))) + ' - ' + COINDATA[allCoins[i]].Name()
            if len(coinSymbolLong) > FIELD_LENGTH - 1:
                coinSymbolLong = coinSymbolLong[0:FIELD_LENGTH-1]
                coinSymbolLong = coinSymbolLong[:-2] + '.'

            coinSymbolLong += ' ' * ( FIELD_LENGTH - len(coinSymbolLong)) 

            coinSymbolLong += COINDATA[allCoins[i]].Usd()[:9]

            xx = i % ( y - 3 );
            yy = (i - xx) / ( y - 3 );

            stdscr.addnstr( xx + 2 ,yy * (FIELD_LENGTH + 10), coinSymbolLong, x, curses.color_pair(3) )
    else:
        stdscr.clear()

        stdscr.addnstr( 0,0, ASCIIART1, x, curses.color_pair(4))
        stdscr.addnstr( 1,0, ASCIIART2, x, curses.color_pair(4))
        stdscr.addnstr( 2,0, ASCIIART3, x, curses.color_pair(4))
        stdscr.addnstr( 3,0, ASCIIART4, x, curses.color_pair(4))

        header = 'COIN%sPRICE%sHOLDING%sWORTH%sCHANGE 1H%sCHANGE 24H%s' % ( spacer_for_4,
                                                                            spacer_for_5,
                                                                            spacer_for_7,
                                                                            spacer_for_5,
                                                                            spacer_for_9,
                                                                            spacer_for_10) 
        
        
        stdscr.addnstr( 5,0, header, x, curses.color_pair(4) )
        stdscr.addnstr( 5,SORTING * FIELD_LENGTH + FIELD_LENGTH - 2, 'v', x, curses.color_pair(4) )

        allCoins = list(WALLET.keys())
        numCoins = len(allCoins)

        listEntrys = []
        total = 0
        for i in range(numCoins):
            if not allCoins[i] in COINDATA:
                #DoRemoveCoin(allCoins[i]) # do this if you dont want the somehow  removed coin to stay in the wallet
                continue
            
            coinSymbol = allCoins[i]
            coinSymbolLong = coinSymbol + (' ' * (5 - len(coinSymbol))) + ' - ' + COINDATA[allCoins[i]].Name()
            if len(coinSymbolLong) > FIELD_LENGTH - 1:
                coinSymbolLong = coinSymbolLong[0:FIELD_LENGTH-1]
                coinSymbolLong = coinSymbolLong[:-2] + '.'

            coinUsdValue = COINDATA[allCoins[i]].Usd()
            holding  = float(WALLET[coinSymbol])
            holdingStr = WALLET[coinSymbol]
            worth = holding * float(coinUsdValue)
            worthStr = str(worth)
            change1h = COINDATA[allCoins[i]].Change1h()
            change24h = COINDATA[allCoins[i]].Change24h()

            total += worth

            spacer1 = ' ' * ( FIELD_LENGTH - len(coinSymbolLong) )
            spacer2 = ' ' * ( FIELD_LENGTH - len(coinUsdValue))
            spacer3 = ' ' * ( FIELD_LENGTH - len(holdingStr))
            spacer4 = ' ' * ( FIELD_LENGTH - len(worthStr))
            spacer5 = ' ' * ( FIELD_LENGTH - len(change1h))
            spacer6 = ' ' * ( FIELD_LENGTH - len(change24h))

            candidate = '%s%s%s%s%s%s%s%s%s%s%s%s' % ( coinSymbolLong,spacer1,coinUsdValue,spacer2,holdingStr,spacer3, worthStr, spacer4, change1h, spacer5, change24h, spacer6 )
            
            listEntrys.append( [candidate, coinSymbol, float(coinUsdValue), holding, worth, float(change1h), float(change24h)] )


        listEntrys.sort(key=lambda r:r[1+SORTING])
        for i in range(len(listEntrys)):
            stdscr.addnstr( i + 6,0, listEntrys[i][0], x, curses.color_pair(3 - (i % 2)) )


        balanceTag = 'TOTAL BALANCE: '
        balance = '$%s' % str(total)
        stdscr.addnstr( y-4,0, balanceTag, x, curses.color_pair(2) )
        stdscr.addnstr( y-4,len(balanceTag), balance, x, curses.color_pair(3) )


        # BUTTON management
        DrawMenu(stdscr, y, x)



def AddCoin(stdscr):
    inputData = ReadStringFromCmd(stdscr, 'Enter Symbol , and Amount ( BTC,2.45 )').strip().upper()
    if ',' in inputData:
        symbol, amount = inputData.split( ',' )

        symbol = symbol.strip()
        amount = amount.strip()

        if symbol in COINDATA:
            WALLET[symbol.strip()] = amount.strip()
            WriteWallet()

def RemoveCoin(stdscr):
    inputData = ReadStringFromCmd(stdscr, 'What Symbol do you want to remove?').strip().upper()
    DoRemoveCoin(inputData)

def DoRemoveCoin(c):
    if c in WALLET:
        WALLET.pop(c)
        WriteWallet()

def MenuActivate( stdscr ):
    if CURRENTMENU == 0:
        AddCoin(stdscr)
    elif CURRENTMENU == 1:
        RemoveCoin(stdscr)
    elif CURRENTMENU == 2:
        global DRAWLIST
        DRAWLIST = not DRAWLIST
    elif CURRENTMENU == 3:
        global SORTING
        SORTING += 1
        if SORTING >= 6:
            SORTING = 0;
    elif CURRENTMENU == 4:
        sys.exit(0)

def Mainc(stdscr):
    global CURRENTMENU
    inputKey = 0
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    textColor = getattr(curses, 'COLOR_GREEN' )
    highlightTextColor = getattr(curses, 'COLOR_WHITE' )
    backgroundColor = getattr(curses, 'COLOR_BLACK' )


    curses.init_pair(2, textColor, backgroundColor)
    curses.init_pair(3, backgroundColor, textColor)
    curses.init_pair(4, highlightTextColor, backgroundColor)
    curses.init_pair(5, backgroundColor, highlightTextColor)

    global DRAWLIST
    DRAWLIST = False

    curses.halfdelay(10)

    y, x = stdscr.getmaxyx()
    stdscr.clear()

    while inputKey not in {KEY_ESCAPE, KEY_Q, KEY_q}:
        UpdateCoindata()
        while True:
            try:
                Draw(stdscr, y, x)
            except curses.error:
                pass

            inputKey = stdscr.getch()
            if inputKey != curses.KEY_RESIZE:
                break
            stdscr.erase()
            y, x = stdscr.getmaxyx()

        if inputKey in {KEY_a, KEY_A}:
            AddCoin(stdscr)

        if inputKey in {KEY_r, KEY_R}:
            RemoveCoin(stdscr)
       
        if inputKey in {KEY_l, KEY_L}:
            DRAWLIST = not DRAWLIST

        if inputKey in {KEY_c, KEY_C}:
            global SORTING
            SORTING += 1
            if SORTING >= 6:
                SORTING = 0;

        if inputKey in {KEY_RIGHT}:
            CURRENTMENU += 1
            if CURRENTMENU >= len(BUTTONS):
                CURRENTMENU = 0

        if inputKey in {KEY_LEFT}:
            CURRENTMENU -= 1
            if CURRENTMENU < 0:
                CURRENTMENU = len(BUTTONS) - 1

        if inputKey in {KEY_ENTER}:
            MenuActivate(stdscr)

def Main():
    try:
        os.makedirs(BASEDIR)
    except:
        pass

    global WALLET
    WALLET = ReadWallet()
    global CURRENTMENU
    CURRENTMENU = 0

    global SORTING
    SORTING = 3
    curses.wrapper(Mainc)


if __name__ == '__main__':
    Main()
