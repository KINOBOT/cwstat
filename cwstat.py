import requests
import json
import curses
import os, sys
import threading
import datetime


#GLOBAL VARIABLES
KEY_ESCAPE = 27
KEY_ZERO = 48
KEY_A = 65
KEY_L = 76
KEY_Q = 81
KEY_R = 82
KEY_S = 83
KEY_C = 67
KEY_W = 87
KEY_a = 97
KEY_l = 108
KEY_q = 113
KEY_r = 114
KEY_s = 115
KEY_c = 99
KEY_w = 119
KEY_LEFT = 260
KEY_RIGHT = 261
KEY_ENTER = 10

COINDATA = {}

FIELD_LENGTH = 20
BUTTONS = [ '[A] Add/Modify Coin ', '[R] Remove Coin ', '[L] List all Coins ', '[C] Cycle Sorting ', '[W] Cycle Wallets ', '[Q] Quit ']

USAGE = '[<>] to navigate [ENTER] to select'

BASEDIR = os.path.join(os.path.expanduser('~'), '.cwstat')
#WALLETFILE = os.path.join(BASEDIR, 'wallet.json')


ASCIIART1 = '   __ _______  ______  ___  ____ ______                      __       __       '
ASCIIART2 = '  / //_/  _/ |/ / __ \/ _ )/ __ /_  __/ ____  _____    _____/ /____ _/ /_  ____'
ASCIIART3 = ' / .< _/ //    / /_/ / _  / /_/ // /   /___/ / __| |/|/ (_-/ __/ _ `/ __/ /___/'
ASCIIART4 = '/_/|_/___/_/|_/\____/____/\____//_/          \__/|__/__/___\__/\___/\__/       '
 
PRUNELIST = { 'batcoin' }

class Coin:
    def __init__(self):
        self.data = ''

    def __init__(self, jsondata ):
        self.data = jsondata

    def Id( self ):
        return self.data['id']

    def Symbol(self):
        return self.data['symbol']
    
    def Name(self):
        return self.data['name']

    def Usd(self):
        return self.data['price_usd']
    
    def Change1h(self):
        c = self.data['percent_change_1h']
        if not c == None:
            return c
        else:
            return '0.0' 

    def Change24h(self):
        c = self.data['percent_change_24h']
        if not c == None:
            return c
        else:
            return '0.0' 

def UpdateCoindata():
    # invoke repeating
    global THREADMAIN
    THREADMAIN = threading.Timer( 10.0, UpdateCoindata )
    THREADMAIN.start()

    url = 'https://api.coinmarketcap.com/v1/ticker/?limit=0'

    try:
        r = requests.get(url)
    except requests.exceptions.RequestException:
        sys.exit('Could not get live ticker')

    counter = {}
    try:
        jdata = r.json()
        COINDATA.clear()
        for entry in jdata:
            c = Coin( entry )
            if not c.Id() in PRUNELIST:
                COINDATA[c.Symbol()] = c
    except:
        sys.exit('Could not parse data')


    global LASTUPDATED
    LASTUPDATED = datetime.datetime.now()
    

def WriteWallets():
    global WALLETS
    for i in range(len(WALLETS)):
        outpath = os.path.join(BASEDIR, 'wallet_%s.json' % i ) 
        print outpath
        WriteWallet( WALLETS[i], outpath )

def WriteWallet( wal, outfile ):
    with open(outfile, 'w') as f:
        json.dump(wal, f)

def ReadWallets():
    global WALLETS
    WALLETS = []
    for f in sorted(os.listdir( BASEDIR )):
        if f.endswith( '.json'):
            WALLETS.append( ReadWallet(os.path.join( BASEDIR, f )) )

def ReadWallet(infile):
    try:
        with open(infile, 'r') as f:
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
    global DRAWLISTID
    global WALLETS
    global CURRENTWALLET
    global LASTUPDATED


    if len(WALLETS) > 0:
        wallet = WALLETS[CURRENTWALLET]
    else:
        wallet = {}
        WALLETS.append(wallet)

    if DRAWLIST:
        stdscr.clear()
        global DRAWLISTID
        global LISTITEMSPERSCREEN
        global DRAWLISTMAX
        stdscr.addnstr( 0, 0, 'AVAILABLE COINS ( page ' + str(DRAWLISTID+1) + ' of ' + str(DRAWLISTMAX) + ' )' , x, curses.color_pair(4) )
        stdscr.addnstr( y - 1, 0, "[L] to go back", x, curses.color_pair(2) )

        allCoins = list(COINDATA.keys())
        allCoins.sort()
        listStart = DRAWLISTID * LISTITEMSPERSCREEN
        listEnd =   listStart  + LISTITEMSPERSCREEN
        allCoins = allCoins[int(listStart):int(listEnd)]
        numCoins = len(allCoins)

        for i in range(numCoins):
            coinSymbol = allCoins[i]
            coinSymbolLong = coinSymbol + (' ' * (5 - len(coinSymbol))) + ' - ' + COINDATA[allCoins[i]].Name()
            if len(coinSymbolLong) > FIELD_LENGTH - 1:
                coinSymbolLong = coinSymbolLong[0:FIELD_LENGTH-1]
                coinSymbolLong = coinSymbolLong[:-2] + '.'

            coinSymbolLong += ' ' * ( FIELD_LENGTH - len(coinSymbolLong)) 


            coinValue = COINDATA[allCoins[i]].Usd()
            if not coinValue == None:
                coinSymbolLong += coinValue;

            if len(coinSymbolLong) > FIELD_LENGTH + 9:
                coinSymbolLong = coinSymbolLong[:FIELD_LENGTH + 8]


            xx = i % ( y - 3 )
            yy = (i - xx) / ( y - 3 )

            colorId = 3 - ( xx % 2 )
	    if allCoins[i] in wallet:
	        colorId = 5

            stdscr.addnstr( xx + 2 ,int(yy * (FIELD_LENGTH + 10)), coinSymbolLong, x, curses.color_pair(colorId) )
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

        stdscr.addnstr( 4,0, 'Wallet %s / %s' % (CURRENTWALLET + 1, len(WALLETS)), x, curses.color_pair(4) )
        stdscr.addnstr( 5,0, header, x, curses.color_pair(4) )
        stdscr.addnstr( 5,SORTING * FIELD_LENGTH + FIELD_LENGTH - 2, 'v', x, curses.color_pair(4) )

        allCoins = list(wallet.keys())
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
            holding  = float(wallet[coinSymbol])
            holdingStr = wallet[coinSymbol]
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

        updateTimeStr = LASTUPDATED.strftime( '%c')
        stdscr.addnstr( y-4,len(balanceTag) + len(balance) + 2, updateTimeStr , x, curses.color_pair(2) )


        # BUTTON management
        DrawMenu(stdscr, y, x)



def AddCoin(stdscr):
    inputData = ReadStringFromCmd(stdscr, 'Enter Symbol , and Amount ( BTC,2.45 )').strip().upper()
    if ',' in inputData and len(inputData.split( ',' )) == 2:
        symbol, amount = inputData.split( ',' )

        if symbol == '' or amount == '':
            return

        symbol = symbol.strip()
        amount = amount.strip()

        if symbol in COINDATA:
            global WALLETS
            global CURRENTWALLET
            if len(WALLETS) > 0:
                w = WALLETS[CURRENTWALLET]
            else:
                w = {}
                WALLETS.append(w)
            w[symbol.strip()] = amount.strip()
            WriteWallets()

def RemoveCoin(stdscr):
    inputData = ReadStringFromCmd(stdscr, 'What Symbol do you want to remove?').strip().upper()
    DoRemoveCoin(inputData)

def DoRemoveCoin(c):
    global WALLETS
    global CURRENTWALLET
    if len(WALLETS) > 0:
        w = WALLETS[CURRENTWALLET]
    else:
        w = {}
        WALLETS.append(w)

    if c in w:
        w.pop(c)
        WriteWallets()

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
        global CURRENTWALLET
        global WALLETS
        CURRENTWALLET += 1
        if ( CURRENTWALLET >= len(WALLETS)):
            CURRENTWALLET = 0
    elif CURRENTMENU == 5:
        global THREADMAIN
        THREADMAIN.cancel()
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

    global DRAWLISTID
    DRAWLISTID = 0
    itemsPerListColumn = y - 3
    columnsPerScreen = x / (FIELD_LENGTH + 10 )
    global LISTITEMSPERSCREEN
    LISTITEMSPERSCREEN = itemsPerListColumn * columnsPerScreen
    global DRAWLISTMAX
    DRAWLISTMAX = int(( len(COINDATA) / LISTITEMSPERSCREEN ) + 1 )

    global SORTING
    global CURRENTWALLET
    global WALLETS

    while inputKey not in {KEY_ESCAPE, KEY_Q, KEY_q}:
        while True:
            try:
                Draw(stdscr, y, x)
            except curses.error:
                THREADMAIN.cancel()
                pass

            inputKey = stdscr.getch()
            if inputKey != curses.KEY_RESIZE:
                itemsPerListColumn = y - 3
                columnsPerScreen = x / (FIELD_LENGTH + 10 )
                LISTITEMSPERSCREEN = itemsPerListColumn * columnsPerScreen
                DRAWLISTMAX = int(( len(COINDATA) / LISTITEMSPERSCREEN ) + 1 ) 
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
            
            SORTING += 1
            if SORTING >= 6:
                SORTING = 0;

        if inputKey in {KEY_w}:
            CURRENTWALLET += 1
            if ( CURRENTWALLET >= len(WALLETS)):
                CURRENTWALLET = 0

        if inputKey in {KEY_W}:
            WALLETS.append({})
            CURRENTWALLET = len(WALLETS) - 1

        if inputKey in {KEY_RIGHT}:
            if not DRAWLIST:
                CURRENTMENU += 1
                if CURRENTMENU >= len(BUTTONS):
                    CURRENTMENU = 0
            else:
                DRAWLISTID += 1
                if DRAWLISTID >= DRAWLISTMAX:
                    DRAWLISTID = 0

        if inputKey in {KEY_LEFT}:
            if not DRAWLIST:
                CURRENTMENU -= 1
                if CURRENTMENU < 0:
                    CURRENTMENU = len(BUTTONS) - 1
            else:
                DRAWLISTID -= 1
                if DRAWLISTID < 0:
                    DRAWLISTID = DRAWLISTMAX - 1

        if inputKey in {KEY_ENTER}:
            MenuActivate(stdscr)

    THREADMAIN.cancel()


def Main():
    try:
        os.makedirs(BASEDIR)
    except:
        pass

    # backwards compatible
    if os.path.isfile( os.path.join( BASEDIR, 'wallet.json')):
        os.rename( os.path.join( BASEDIR, 'wallet.json'), os.path.join( BASEDIR, 'wallet_0.json'))
        
    ReadWallets()
    global CURRENTMENU
    CURRENTMENU = 0

    global CURRENTWALLET
    CURRENTWALLET = 0

    global SORTING
    SORTING = 3

    # intiial update
    UpdateCoindata()

    try:
        curses.wrapper(Mainc)
    except KeyboardInterrupt:
        print 'Interrupted'
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == '__main__':
    Main()
