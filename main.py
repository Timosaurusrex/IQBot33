import requests
import websocket
import sys
from ces import *
from multiprocessing import *
from binance.client import Client
from telegram import *
import time

print("writen by Handschuh Christoph and Timo Perzi <3")
symbol = ""
bricks = ""
last_message = ""
last_date = ""
sar = 0
trend = 0
run = True
mtg = 5

trades = []
trades_price = []
trades_price2 = []
banned_coins = []
high_banned_coins = []

client = Client(api_key="", api_secret="")

def ema_func():
    global bricks
    ema = 0
    for i in range(len(bricks) - 399, len(bricks) - 199):
        ema = float(bricks[i][4]) + ema
    ema = ema / 200

    for i in range(len(bricks) - 199, len(bricks)):
        ema = (float(bricks[i][4]) * (2 / 201)) + (ema * (1 - (2 / 201)))
    print(ema)
    if float(bricks[len(bricks) - 1][4]) > ema:
        return True
    else:
        return False

def macd_func():
    global bricks
    ema_fast = 0
    ema_slow = 0
    for i in range(len(bricks) - 23, len(bricks) - 11):
        ema_fast = float(bricks[i][4]) + ema_fast
    ema_fast = ema_fast / 12

    for i in range(len(bricks) - 51, len(bricks) - 25):
        ema_slow = float(bricks[i][4]) + ema_slow
    ema_slow = ema_slow / 26

    for i in range(len(bricks) - 11, len(bricks)):
        ema_fast = (float(bricks[i][4]) * (2 / 13)) + (ema_fast * (1 - (2 / 13)))

    for i in range(len(bricks) - 25, len(bricks)):
        ema_slow = (float(bricks[i][4]) * (2 / 27)) + (ema_slow * (1 - (2 / 27)))

    if ema_fast - ema_fast/200 > ema_slow:
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

def telegram():
    global last_message, last_date, mtg, run
    message = check_for_message().lower()
    date = check_for_message_date()

    if date != last_date:
        print(message)

        if message == "/end":
            send_message("Beendet")
            last_message = ""

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

        elif message == "help" or message == "/help":
            print("help")
            send_message("Start - /start\nStop - /stop\nMoney - /wallet\nHistory - /history\nSettings - /settings")

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

def coins_info():
    global mtg, trades, trades_price, trades_price2

    with open("bought_coins.txt", "r+") as f:
        i = -1
        j = 0
        for line in f.readlines():
            line = line.strip()
            if i == -1:
                mtg = float(line)  # mtg
            elif i == 0:
                trades.append(line.lower())  # symbol
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

def save_trades():
    global trades_price, trades_price2, trades, mtg

    with open("bought_coins.txt", "r+") as f:
        f.truncate()
        f.write(str(mtg) + "\n")  #mtg
        i = len(trades)-1
        while i >= 0:
            f.write(trades[i].upper() + "\n") #symbol
            with open("coins/" + trades[i] + ".txt", "r+") as d: #Coin holding
                f.write(d.read() + "\n")
            f.write(str(trades_price[i]) + "\n")  #sell price +
            f.write(str(trades_price2[i]) + "\n")  # sell price -
            i -= 1

def coin_sell():
    global trades, trades_price, trades_price2, banned_coins

    print("sell")
    i = len(trades) - 1
    while i >= 0:
        price = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + trades[i].upper()).json()
        price = float(price['price'])
        print(trades[i], price)
        print(1)
        if float(price) < float(trades_price[i]) or float(price) > float(trades_price2[i]):
            sell_all(trades[i])
            print(2)
            with open("history.txt", "a") as f:
                f.write("Sell - " + trades[i] + "  " + str(price) + "\n")

            banned_coins.append(symbol.upper())
            print(1)
            print(trades[i], "Sold")
            trades.pop(i)
            trades_price.pop(i)
            trades_price2.pop(i)
            print(3)

            save_trades()
            i = len(trades)
        i -= 1

def coin_buy():
    global trades, trades_price, trades_price2, banned_coins, bricks, mtg, trend

    print("buy")
    if len(trades) < mtg and trend == 1:
        with open("coin_list.txt") as f:
            for line in f:
                symbol = line.strip()
                contains = True
                reason = False
                bricks = requests.get('https://api.binance.com/api/v1/klines?symbol=' + symbol.upper() + '&interval=30m').json()  # Todo: Timeframe Limit

                if len(trades) < mtg and ema_func() and sar_func() and macd_func():
                    for coin in banned_coins:
                        if coin.upper() == symbol.upper():
                            reason = True

                    if reason == False:
                        contains = False
                        for i in trades:
                            if i.upper() == symbol.upper():
                                contains = True
                else:
                    for coin in banned_coins:
                        if coin.upper() == symbol.upper():
                            banned_coins.remove(symbol.upper())

                if contains == False:
                    trades.append(symbol.upper())
                    print(trades)
                    trades_price.append(sar)
                    trades_price2.append((float(bricks[len(bricks) - 1][4]) - sar) + float(bricks[len(bricks) - 1][4]))
                    buy(symbol, Quantity(symbol, mtg))
                    f = open("history.txt", "a")
                    f.write("Buy - " + symbol + "  " + bricks[len(bricks) - 1][4] + " - " + str(sar) + " - " + str((float(bricks[len(bricks) - 1][4]) - sar) + float(bricks[len(bricks) - 1][4])) + "\n")
                    f.close()
                    print(symbol, "bought, Sellprice = ", str(sar), str((float(bricks[len(bricks) - 1][4]) - sar) + float(bricks[len(bricks) - 1][4])))
                    save_trades()

    elif len(trades) == 0 and trend == 0:
        time.sleep(20)

def second_strategy(symbol):
    global bricks, high_banned_coins, mtg

    if 12 >= ((float(bricks[499][4]) * 100) / float(bricks[451][4]) - 100) and mtg < len(trades):
        high_banned_coins.pop(symbol.upper())

    # am besten 5min oder sofort den derzeitigen Wert, das er beim höchsten Punkt verkauft, das es wieder gelöscht wird
    if 17 <= ((float(bricks[499][4]) * 100) / float(bricks[451][4]) - 100) and mtg < len(trades):
        i = len(high_banned_coins) - 1
        while i >= 0:
            if symbol.upper() == high_banned_coins[i]:
                trades.append(symbol.upper())
                print(trades)
                price = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + trades[i].upper()).json()
                price = float(price['price'])
                trades_price.append(price * 0.98)
                trades_price2.append(price * 1.03)
                buy(symbol, Quantity(symbol, mtg))
                f = open("history.txt", "a")
                f.write("Buy - " + symbol + "  " + str(price) + " - " + str(price * 0.98) + " - " + str(price * 1.03) + "\n")
                f.close()
                print(symbol, "bought, Sellprice = ", str(price * 0.98), str(price * 1.03))
                save_trades()
                high_banned_coins.append(symbol.upper())

if __name__ == '__main__':

    with open("coin_list.txt", "r+") as f:
        zeile = 0
        x = 0
        for line in f:
            symbol = line.strip().lower()
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
                banned_coins.append(symbol.upper())

            if 18 <= ((float(bricks[499][4]) * 100) / float(bricks[451][4]) - 100):
                high_banned_coins.append(symbol.upper())
            x += 1
            print(x)
    print(f"banned_coins: {banned_coins}")

    coins_info()

    while True:
        start = time.time()

        telegram()

        with open("distribution.txt", "r") as f:
            trend = float(f.readline())

        if trend == 0:
            with open("coin_list.txt", "r+") as f:
                for line in f:
                    symbol = line.strip().lower()

                    brick = requests.get('https://api.binance.com/api/v1/klines?symbol=' + symbol.upper() + '&interval=30m')  # Todo: Timeframe Limit
                    bricks = brick.json()

                    if macd_func() and ema_func() and sar_func():
                        banned_coins.append(symbol.upper())

                    second_strategy(symbol.upper())
        else:
            coin_buy()
        coin_sell()

        ende = time.time()
        print('{:5.3f}s'.format(ende - start))


"""
#runInParallel(, , coin_sell)

        p1 = Process(target=coins_distribution)
        p1.start()
        p2 = Process(target=coin_buy)
        p2.start()
        p3 = Process(target=coin_sell)
        p3.start()

        p1.join()
        p2.join()
        p3.join()

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
            coins_info()
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

            for j in trades:
                symbolprice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + j.upper()).json()
                symbolprice = float(symbolprice["price"])
                f = open("coins/" + j.upper() + ".txt", 'r')
                current_value = current_value + (float(f.read()) * float(symbolprice))
                f.close()
            x = requests.post("https://tradingbot.111mb.de//data_ins_christoph.php", data={'key': 'ae9w47', 'value': str(current_value)})
        i -= 1
    ende = time.time()
    print('{:5.3f}s'.format(ende - start))
    sys.exit()

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

    with open("bought_coins.txt", "r") as f:
        send_message(f.read())
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/btcbusd@kline_5m", on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error)
    ws.run_forever()

def on_error(ws, error):
    print(error)
"""

