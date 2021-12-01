print("writen by Handschuh Christoph and Timo Perzi <3")

import requests
import ces

symbol = ""
bricks = ""
sar = 0
run = True

trades = []
trades_price = []
trades_price2 = []
banned_coins = []

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

with open("coin_list.txt") as f:
    for line in f:
        symbol = line.strip()
        bricks = requests.get('https://api.binance.com/api/v1/klines?symbol=' + symbol.upper() + '&interval=30m').json()  # Todo: Timeframe Limit
        if macd_func() and ema_func() and sar_func():
            banned_coins.append(symbol)
print(f"banned_coins: {banned_coins}")

while run:
    if len(trades) < 5:
        with open("coin_list.txt") as f:
            for line in f:
                contains = True
                reason = False
                symbol = line.strip()
                print(symbol)
                bricks = requests.get('https://api.binance.com/api/v1/klines?symbol=' + symbol.upper() + '&interval=30m').json()  # Todo: Timeframe Limit

                if len(trades) < 5 and macd_func() and ema_func() and sar_func():
                    for coin in banned_coins:
                        if coin == symbol:
                            reason = True

                    if reason == False:
                        contains = False
                        for i in trades:
                            if i == symbol:
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
                    ces.buy(symbol, ces.Quantity(symbol, 5))
                    f = open("history.txt", "a")
                    f.write("Buy - " + symbol + "  " + bricks[len(bricks) - 1][4] + " - " + str(sar) + " - " + str((float(bricks[len(bricks) - 1][4]) - sar) + float(bricks[len(bricks) - 1][4])) + "\n")
                    f.close()
                    print(symbol, "bought, Sellprice = ", str(sar), str((float(bricks[len(bricks) - 1][4]) - sar) + float(bricks[len(bricks) - 1][4])))

    i = len(trades) - 1
    while i >= 0:
        price = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + trades[i].upper()).json()
        #price = float(price['price'])
        print(trades[i], price)
        if price < trades_price[i] or price > trades_price2[i]:
            ces.sell_all(trades[i])
            f = open("history.txt", "a")
            f.write("Sell - " + trades[i] + "  " + price + "\n")
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
            for j in trades:
                symbolprice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + j.upper()).json()
                symbolprice = float(symbolprice["price"])
                f = open(j.upper() + ".txt", 'r')
                current_value = current_value + (float(f.read()) * float(symbolprice))
                f.close()
            x = requests.post("https://tradingbot.111mb.de//data_ins_christoph.php",data={'key': 'ae9w47', 'value': str(current_value)})
        i -= 1