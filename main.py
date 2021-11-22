print("writen by Timo Perzi, Lib Telegram, ces by Christoph Handschuh")

from binance.client import Client
from ces import buy, sell, Quantity
import websocket
import json
import requests
import config
from Telegram import send_message, check_for_message, check_for_message_date
import time

class Coin:
    def __init__(self, symbol, sold, y, change):
        self.symbol = symbol
        self.sold = sold
        self.y = y
        self.change = change

list = []
list2 = []
n = 0
buy_price = 0
sell_price = 0
last_message = ""
buy_symbol = "Coin"
run = False
position = False
macd_change = False

last_date = check_for_message_date()
client = Client(config.API_KEY, config.API_SECRET)

with open("coin_list.txt") as f:
    for coin in f:
        coin = coin.strip()
        coinasobject = Coin(coin, True, 0, 0)
        list.append(coinasobject)
        list2.append(coin)
print(list2)

def on_message(ws, msg):
    global ema, ema_old, ema_old_fast, ema_old_slow, macd_line, ema_old_macd
    global position, sar, lowest, highest, quantity, buy_symbol, run
    global macd_change, i, sar_bool, buy_price, sell_price, sold, counter

    if run:
        for Symbol in list:
            i = 0
            ema_old_fast = 0
            ema_old_slow = 0
            ema_old_macd = 0
            ema_old = 0
            lowest = 0
            highest = 0
            counter = 1
            sar = 0
            sar_bool = False
            print(Symbol.symbol.upper())
            time.sleep(1)

            for kline in client.get_historical_klines_generator(Symbol.symbol.upper(), Client.KLINE_INTERVAL_30MINUTE, "20 day ago UTC"):

                i += 1
                price = float(kline[4])
                price_highest = float(kline[2])
                price_lowest = float(kline[3])

                # SAR
                if price_lowest < lowest and sar_bool == True:
                    lowest = price_lowest
                elif price_highest > highest and sar_bool == True:
                    highest = price_highest
                    counter += 1

                if price_lowest < lowest and sar_bool == False:
                    lowest = price_lowest
                    counter += 1
                elif price_highest > highest and sar_bool == False:
                    highest = price_highest

                if sar_bool == False and sar < price_highest:
                    sar_bool = True
                    counter = 1
                    sar = lowest
                    highest = lowest
                elif sar_bool == True and sar > price_lowest:
                    sar_bool = False
                    counter = 1
                    sar = highest
                    lowest = highest

                if sar_bool:
                    sar = sar + (0.02 * counter) * (highest - sar)
                elif sar_bool == False:
                    sar = sar + (0.02 * counter) * (lowest - sar)

                # EMA
                ema = price * (2 / 201) + ema_old * (1 - (2 / 201))
                ema_old = ema

                # MACD
                ema_fast = price * (2 / 13) + ema_old_fast * (1 - (2 / 13))
                ema_old_fast = ema_fast
                ema_slow = price * (2 / 27) + ema_old_slow * (1 - (2 / 27))
                ema_old_slow = ema_slow
                macd_line = ema_fast - ema_slow

                ema_macd = macd_line * (2 / 10) + ema_old_macd * (1 - (2 / 10))
                ema_old_macd = ema_macd
                macd = macd_line - ema_macd

                if i >= 960:
                    """
                    print(kline)
                    print(f"EMA200: {ema}")
                    print(f"MACD: {macd}")
                    print(f"SAR: ({sar_bool}) {sar}")
                    """

                    if ema < price:

                        if macd > 0 and macd_change == False and ema < price_highest and Symbol.y <= 4 and Symbol.sold == False:
                            macd_change = True
                            Symbol.y += 1
                        elif macd < 0 and macd_change == False:
                            macd_change = True
                            Symbol.sold = False
                            Symbol.y = 0

                        if Symbol.change == 0:  # Damit er zu beginn erst beim aufstieg wieder kauft
                            if macd > 0:
                                position = True

                            if macd < 0:
                                if position:
                                    position = False
                                    Symbol.change = 1

                        else:
                            if macd > 0 and macd_change == True:

                                if position:
                                    print("Er scoutet!")

                                elif position == False and sar_bool and Symbol.sold == False:
                                    print("buy")
                                    quantity = float(Quantity(Symbol.symbol.upper()))
                                    buy_price = 2 * price - lowest
                                    sell_price = sar
                                    # client.cancel_order(symbol=Symbol.symbol.upper())
                                    # client.order_market_buy(symbol = symbol.upper(), quantity = float(quantity))
                                    # client.order_limit_sell(symbol=Symbol.symbol.upper(), quantity=float(quantity), price=buy_price)
                                    # client.order_limit_stop(symbol=Symbol.symbol.upper(), quantity=float(quantity), price=sell_price)
                                    # send_message("buy")
                                    buy(Symbol.symbol.upper(), quantity)
                                    buy_symbol = Symbol.symbol
                                    position = True
                                    f = open("OrderHistory.txt", "a")
                                    f.write(f"BUY - {buy_symbol} {str(price)}\n")
                                    f.close()
                    macd_change = False

                if buy_price < price or sell_price > price:
                    if position and buy_symbol == Symbol.symbol:
                        print("sell")
                        #send_message("sell")
                        with open("Coin.txt", 'r+') as f:
                            sell(Symbol.symbol.upper(), float(f.read()))
                        with open("OrderHistory.txt", 'a') as f:
                            f.write(f"SELL - {buy_symbol} - {str(price)}\n")
                        position = False
                        Symbol.sold = True
    telegram()

def telegram():
    global last_message, last_date, buy_symbol, run
    message = check_for_message()
    message = message.lower()
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
            send_message("Money - /wallet\nHistory - /history\nNew Coin - /change_coin\nrestart functions - /functions")
        elif message == "/functions":
            print("secret functions")
            send_message("sell everything - /sell_everything\nrestart OrderHistory - /restart_history\nrestart money - /restart_money")

        elif message == "change coin" or message == "/change_coin":
            f = open("coin_list.txt", "r")
            send_message(f"Coin:\n{f.read()}\nWelchen Coins wollen sie?    /end")
            f.close()
            last_message = message
            print("change coin")
        elif last_message == "/change_coin" or last_message == "change coin" and message != "/end":
            with open("coin_list.txt", 'r+') as f:
                f.write(message)
            with open("Coin", 'r+') as f:
                sell(buy_symbol, float(f.read()))
                f.truncate(0)
            last_message = ""
            send_message("Coin changed!")

        elif message == "restart history" or message == "/restart_history":
            print("restart history")
            with open("OrderHistory.txt", 'r+') as f:
                f.truncate(0)
            last_message = ""
            send_message("!Finished!")

        elif message == "restart money" or message == "/restart_money":
            send_message(f"How much money do you want?    /end")
            last_message = message
            print("restart money")
        elif last_message == "restart money" or last_message == "/restart_money" and message != "/end":
            f = open("COIN.txt", "w")
            f.write("0")
            f.close()
            f = open("USDT.txt", "w")
            f.write(message)
            f.close()
            send_message("!Finished!")

        elif message == "/wallet" or message == "wallet":
            f = open("USDT.txt", "r")
            geld = float(f.read())
            f.close()
            f = open("COIN.txt", "r")
            munze = float(f.read())
            f.close()
            if buy_symbol == "Coin":
                sum = 0
            else:
                munzeprice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + buy_symbol.upper())
                munzeprice = json.loads(munzeprice.text)
                munzeprice = float(munzeprice["price"])
                sum = (geld + (munze * float(munzeprice)))
            send_message(f"USD: {str(geld)}\n{buy_symbol.upper()}: {str(munze)}\nCurrent Value: {str(sum)}")
        elif message == "/history" or message == "history":
            f = open("OrderHistory.txt", "r")
            send_message(f.read())
            f.close()
        last_date = date

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')
    send_message("Er is abgestürzt!!!")
    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error)
    ws.run_forever()

def on_error(ws, error):
    global n
    print(error)
    n += 1
    if n % 30 == 0:
        send_message(error)
        n = 0

SOCKET = "wss://stream.binance.com:9443/ws/btcbusd@kline_1m"
send_message("Do you want to start, press /start ?")
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error)
ws.run_forever()

