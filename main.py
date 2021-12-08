#print("writen by Handschuh Christoph and Timo Perzi <3")

import requests
import websocket
import sys
from ces import *
from multiprocessing import Process
from binance.client import Client
from telegram import *
import time

symbol = ""
bricks = ""
last_message = ""
last_date = ""
sar = 0
save_trend = 0
run = True
trend = False

trades = []
trades_price = []
trades_price2 = []
banned_coins = []

client = Client(api_key="", api_secret="")

def coin_buy():
    global trend, trades, trades_price, trades_price2, banned_coins
    if len(trades) < mtg:
        if trend == False:
            with open("coin_list.txt") as f:
                for line in f:
                    symbol = line.strip()
                    contains = True
                    reason = False
                    bricks = requests.get('https://api.binance.com/api/v1/klines?symbol=' + symbol.upper() + '&interval=30m').json()  # Todo: Timeframe Limit

                    if len(trades) < mtg and ema_func() and sar_func() and macd_func():
                        for coin in banned_coins:
                            if coin == symbol:
                                reason = True

                        if reason == False:
                            contains = False
                            for i in trades:
                                if i.lower() == symbol.lower():
                                    contains = True
                    else:
                        for coin in banned_coins:
                            if coin == symbol:
                                banned_coins.remove(symbol)

                    if contains == False:
                        trades.append(symbol)
                        print(trades)
                        trades_price.append(sar)
                        trades_price2.append((float(bricks[len(bricks) - 1][4]) - sar) + float(bricks[len(bricks) - 1][4]))
                        buy(symbol, Quantity(symbol, mtg))
                        f = open("history.txt", "a")
                        f.write("Buy - " + symbol + "  " + bricks[len(bricks) - 1][4] + " - " + str(sar) + " - " + str((float(bricks[len(bricks) - 1][4]) - sar) + float(bricks[len(bricks) - 1][4])) + "\n")
                        f.close()
                        print(symbol, "bought, Sellprice = ", str(sar), str((float(bricks[len(bricks) - 1][4]) - sar) + float(bricks[len(bricks) - 1][4])))
                        save_trades()

def coins_distribution():
    global save_trend, trend

    print("coin_distribution")
    with open("coin_list.txt", "r+") as f:
        points = 0
        for line in f:
            symbol = line.strip()
            brick = requests.get('https://api.binance.com/api/v1/klines?symbol=' + symbol.upper() + '&interval=5m')  # Todo: Timeframe Limit
            bricks = brick.json()
            percent = (float(bricks[499][4]) * 100) / float(bricks[211][4]) - 100

            if percent >= 10:
                points = points + 6
                #print(symbol.upper())
            elif percent < 10 and percent >= 7:
                points = points + 4
            elif percent < 7 and percent >= 5:
                points = points + 3
            elif percent < 5 and percent >= 3:
                points = points + 2
            elif percent < 3 and percent > 0:
                points = points + 1
            elif percent < 0 and percent >= -3:
                points = points - 1
            elif percent < -3 and percent >= -5:
                points = points - 2
            elif percent < -5 and percent >= -7:
                points = points - 4
            elif percent < -7 and percent > -10:
                points = points - 8
            elif percent <= -10 and percent > -30:
                points = points - 16
            elif percent <= -30:
                points = points - 25

    if points <= 100 and points >= -100:
        points = 0
    elif points <= 600 and points > 100:
        points = 1
    elif points > 600:
        points = 2
    elif points < -100 and points >= -800:
        points = -1
    elif points < -800:
        points = -2

    if points == 2 or (points == 1 and save_trend == 0 or save_trend == -1 or save_trend == -2):
        save_trend = points
        trend = True
    else:
        trend = False

def coins_checking():
    global mtg, trades, trades_price, trades_price2
    with open("bought_coins.txt", "r+") as f:
        i = -1
        j = 0
        for line in f.readlines():
            line = line.strip()
            if i == -1:
                mtg = float(line)  # mtg
            elif i == 0:
                trades.append(line)   # symbol
            elif i == 1:
                with open("coins/" + trades[j].upper() + ".txt", "w") as d:  # Coin holding
                    d.write(line)
                j += 1
            elif i == 2:
                trades_price.append(float(line))  # sell price -
                print(trades_price)
            elif i == 3:
                trades_price2.append(float(line))  # sell price +
                print(trades_price2)
            i += 1
            if i == 4:
                i = 0

def ema_func():
    global bricks
    ema = 0
    for i in range(len(bricks) - 200, len(bricks)):
        ema = float(bricks[i][4]) + ema
    ema = ema / 200

    for i in range(len(bricks) - 200, len(bricks)):
        ema = (float(bricks[i][4]) * (2 / 201)) + (ema * (1 - (2 / 201)))
    if float(bricks[len(bricks) - 1][4]) > ema:
        return True
    else:
        return False

def macd_func():
    global bricks
    ema_fast = 0
    ema_slow = 0
    for i in range(len(bricks) - 9, len(bricks)):
        ema_fast = float(bricks[i][4]) + ema_fast
    ema_fast = ema_fast / 9

    for i in range(len(bricks) - 26, len(bricks)):
        ema_slow = float(bricks[i][4]) + ema_slow
    ema_slow = ema_slow / 26

    for i in range(len(bricks) - 12, len(bricks)):
        ema_fast = (float(bricks[i][4]) * (2 / 13)) + (ema_fast * (1 - (2 / 13)))

    for i in range(len(bricks) - 26, len(bricks)):
        ema_slow = (float(bricks[i][4]) * (2 / 27)) + (ema_slow * (1 - (2 / 27)))

    if ema_fast > ema_slow:
        return True
    else:
        return False

def sar_func():
    global bricks, sar
    sar_bool = False
    lowest = 0
    highest = 0
    counter = 1

    for i in range(len(bricks) - 200, len(bricks)):
        price_highest = float(bricks[i][2])
        price_lowest = float(bricks[i][3])

        if price_highest > highest and sar_bool:
            highest = price_highest
            if counter < 10:
                counter += 1

        if price_lowest < lowest and sar_bool == False:
            lowest = price_lowest
            if counter < 10:
                counter += 1

        if sar_bool == False and sar < price_highest:
            sar_bool = True
            counter = 1
            sar = lowest
            highest = lowest
        elif sar_bool and sar > price_lowest:
            sar_bool = False
            counter = 1
            sar = highest
            lowest = highest

        if sar_bool:
            sar = sar + (0.02 * counter) * (highest - sar)
        else:
            sar = sar + (0.02 * counter) * (lowest - sar)

    return sar_bool

def remove_line(fileName, lineToSkip): #Removes a given line from a file
    with open(fileName, 'r') as read_file:
        lines = read_file.readlines()

    currentLine = 1
    with open(fileName, 'w') as write_file:
        for line in lines:
            if currentLine == lineToSkip:
                pass
            else:
                write_file.write(line)
            currentLine += 1

def runInParallel(*fns):
  proc = []
  for fn in fns:
    p = Process(target=fn)
    p.start()
    proc.append(p)
  for p in proc:
    p.join()

def save_trades():
    global trades_price, trades_price2, trades, mtg

    with open("bought_coins.txt", "r+") as f:
        f.write(str(mtg) + "\n")  #mtg
        i = len(trades)-1
        while i >= 0:
            f.write(trades[i].lower() + "\n") #symbol
            with open("coins/" + trades[i] + ".txt", "r+") as d: #Coin holding
                f.write(d.read() + "\n")
            f.write(str(trades_price[i]) + "\n")  #sell price +
            f.write(str(trades_price2[i]) + "\n")  # sell price -
            i -= 1

def telegram():
    global last_message, last_date, run, mtg
    message = check_for_message()
    message = message.lower()
    date = check_for_message_date()

    if date != last_date:
        print(message)
        if message == "/end":
            send_message("Beendet")
            last_message = ""

        elif message == "help" or message == "/help":
            print("help")
            send_message("Start - /start\nStop - /stop\nMoney - /wallet\nHistory - /history\nSettings - /settings\nNew Coin - /change_coin\nNew Coin later- /change_coin_later\nNew calculate Quantity - /calculate_quantity\nrestart functions - /functions")
        elif message == "/functions":
            print("secret functions")
            send_message("restart OrderHistory - /restart_history\nrestart money - /restart_everything")

        elif message == "stop" or message == "/stop":
            print("stop")
            if run:
                send_message("stopped")
            else:
                send_message("already stopped")
            run = False
            last_message = message
        elif message == "start" or message == "/start":
            if run:
                send_message("already started")
            else:
                send_message("started")
            print("start")
            run = True
            last_message = message

        elif message == "settings" or message == "/settings":
            with open("bought_coins.txt", "r+") as f:
                send_message(f"Setting:\n{f.read()}\nSettings ändern sie?    /end")
            last_message = message
            print("settings")
        elif last_message == "/settings" or last_message == "settings" and message != "/end" and message != "/wallet" and message != "/help":
            with open("bought_coins.txt", 'r+') as f:
                f.write(message)
            coins_checking()
            last_message = ""
            send_message("Settings changed!")

        elif message == "restart history" or message == "/restart_history":
            print("restart history")
            with open("history.txt", 'r+') as f:
                f.truncate(0)
            last_message = ""
            send_message("!Finished!")

        elif message == "restart everything" or message == "/restart_everything":
            send_message(f"How much money do you want?    /end")
            last_message = message
            print("restart money")
        elif last_message == "restart everything" or last_message == "/restart_everything" and message != "/end":
            with open("coin_list.txt", "r+") as f:
                for line in f:
                    with open("coins/" + line.strip().upper() + ".txt", "w") as d:
                        d.write(str(0))
            with open("bought_coins.txt.txt", "r+") as f:
                f.truncate(mtg)
            f = open("USDT.txt", "w")
            f.write(message)
            f.close()
            last_message = ""
            send_message("!Finished!")

        elif message == "/wallet" or message == "wallet":
            with open("USDT.txt", "r") as f:
                geld = float(f.read())
            current_value = 0
            i = len(trades) - 1
            while i >= 0:
                price = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + trades[i].upper()).json()
                price = float(price['price'])
                print(price)
                with open("coins/" + trades[i].upper() + ".txt", 'r') as f:
                    current_value = current_value + (float(f.read()) * price)
                i -= 1
            send_message(f"USD: {str(geld)}\nCoins: \nCurrent Value: {str(current_value + geld)}")
            last_message = ""

        elif message == "/history" or message == "history":
            f = open("history.txt", "r")
            send_message(str(f.read()))
            f.close()

        elif message == "//kill":
            send_message("Good buy Motherfucker <3")
            last_message = message
            sys.exit(0)
        last_date = date

def func1():
  print('func1: starting')
  for i in range(1000000):
    print(i)
    i += 1
    pass
  print('func1: finishing')

def func2():
  print('func2: starting')
  for i in range(1000000):
    print("a")
    i += 1
  print('func2: finishing')

def on_message(ws, msg):
    global trend, trades, trades_price, trades_price2, banned_coins, start, trend

    runInParallel(func1, func2)

    print(f"Derzeitige Markt: {trend}")

    i = len(trades) - 1
    while i >= 0:
        price = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + trades[i].upper()).json()
        price = float(price['price'])
        print(trades[i], price)

        if float(price) < float(trades_price[i]) or float(price) > float(trades_price2[i]):
            sell_all(trades[i])
            f = open("history.txt", "a")
            f.write("Sell - " + trades[i] + "  " + str(price) + "\n")
            f.close()
            banned_coins.append(symbol)
            print(trades[i], "Sold")
            trades.pop(i)
            trades_price.pop(i)
            trades_price2.pop(i)
            i -= 1
            f = open("USDT.txt", "r")
            current_value = float(f.read())
            f.close()
            save_trades()
            """
            for j in trades:
                symbolprice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + j.upper()).json()
                symbolprice = float(symbolprice["price"])
                f = open("coins/" + j.upper() + ".txt", 'r')
                current_value = current_value + (float(f.read()) * float(symbolprice))
                f.close()
            x = requests.post("https://tradingbot.111mb.de//data_ins_christoph.php", data={'key': 'ae9w47', 'value': str(current_value)})
            """
        i -= 1
    ende = time.time()
    print('{:5.3f}s'.format(ende - start))
    sys.exit()

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')
    """
    with open("bought_coins.txt", "r") as f:
        send_message(f.read())
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/btcbusd@kline_5m", on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error)
    ws.run_forever()
    """

def on_error(ws, error):
    print(error)

if __name__ == '__main__':

    coins_checking()

    with open("coin_list.txt", "r+") as f:
        zeile = 0
        x = 0
        for line in f:
            symbol = line.strip()
            zeile += 1
            with open("coins/" + symbol.upper() + ".txt", "w") as d:
                d.write(str(0))
            try:
                brick = requests.get('https://api.binance.com/api/v1/klines?symbol=' + symbol.upper() + '&interval=30m')  # Todo: Timeframe Limit
                bricks = brick.json()
            except requests.exceptions.RequestException as e:
                print("Error: /n ", e)

            if "Invalid symbol" in brick.text:
                print("removed invalid symbol: ", symbol.upper())
                remove_line("coin_list.txt", zeile)

            elif macd_func() and ema_func() and sar_func():
                banned_coins.append(symbol)
            x += 1
            print(x)
    print(f"banned_coins: {banned_coins}")

    start = time.time()

    #send_message("© Written by Timo Perzi and Christoph Handschuh,\n on 30-11-2021")
    while True:

        runInParallel(coins_distribution, coin_buy, telegram)

        print(f"Derzeitige Markt: {trend}")

        i = len(trades) - 1
        while i >= 0:
            price = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + trades[i].upper()).json()
            price = float(price['price'])
            print(trades[i], price)

            if float(price) < float(trades_price[i]) or float(price) > float(trades_price2[i]):
                sell_all(trades[i])
                f = open("history.txt", "a")
                f.write("Sell - " + trades[i] + "  " + str(price) + "\n")
                f.close()
                banned_coins.append(symbol)
                print(trades[i], "Sold")
                trades.pop(i)
                trades_price.pop(i)
                trades_price2.pop(i)
                i -= 1
                f = open("USDT.txt", "r")
                current_value = float(f.read())
                f.close()
                save_trades()
                """
                for j in trades:
                    symbolprice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + j.upper()).json()
                    symbolprice = float(symbolprice["price"])
                    f = open("coins/" + j.upper() + ".txt", 'r')
                    current_value = current_value + (float(f.read()) * float(symbolprice))
                    f.close()
                x = requests.post("https://tradingbot.111mb.de//data_ins_christoph.php", data={'key': 'ae9w47', 'value': str(current_value)})
                """
            i -= 1
        ende = time.time()
        print('{:5.3f}s'.format(ende - start))
        sys.exit()

#send_message("Bot started! /start")
#ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/btcbusd@kline_5m", on_open=on_open, on_message=on_message, on_close=on_close, on_error=on_error)
#ws.run_forever()