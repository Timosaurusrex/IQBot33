#writen by Christoph Handschuh, am 1.10.2021
#simulate a Crypto-Broker
#Quantity added by Timo Perzi

import requests
import json

fee = 0.1

def buy(symbol, quantity):
    global startcapital, fee
    try:
        f = open("USDT.txt", "r")
        startcapital = float(f.read())
        f.close()
    except IOError:
        f = open("USDT.txt", "w")
        f.write(str(startcapital))
        f.close()
    symbolprice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + symbol.upper())
    symbolprice = json.loads(symbolprice.text)
    symbolprice = float(symbolprice["price"])
    if symbolprice*quantity > startcapital:
        return "You are broke"
    else:
        try:
            f = open("COIN.txt", "r")
            oldquantity = float(f.read())
            f.close()
        except IOError:
            f = open("COIN.txt", "w")
            f.write("0")
            f.close()
            oldquantity = 0
        fee = ((quantity * symbolprice)/100) * fee
        #print(fee)
        f = open("COIN.txt", "w")
        f.write(str(quantity + oldquantity))
        f.close()
        f = open("USDT.txt", "r")
        usdt = float(f.read())
        f.close()
        f = open("USDT.txt", "w")
        f.write(str(usdt - (symbolprice*quantity + fee)))
        f.close()
        return 200

def sell(symbol, quantity):
    f = open("COIN.txt", "r")
    crypto = float(f.read())
    f.close()
    if quantity > crypto:
        return "You are broke"
    else:
        symbolprice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + symbol.upper())
        symbolprice = json.loads(symbolprice.text)
        symbolprice = float(symbolprice["price"])
        usdtcurrent = symbolprice*quantity
        f = open("COIN.txt", "w")
        f.write(str(crypto - quantity))
        f.close()
        f = open("USDT.txt", "r")
        usdt = float(f.read())
        f.close()
        f = open("USDT.txt", "w")
        f.write(str(usdt + usdtcurrent))
        f.close()
        return 200

def Quantity(symbol):
    global sum
    symbolprice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + symbol.upper())
    symbolprice = json.loads(symbolprice.text)
    symbolprice = float(symbolprice["price"])
    f = open("USDT.txt", "r")
    money = float(f.read())
    f.close()
    #print(money/(symbolprice * 1.05))
    sum = money/(symbolprice * 1.05)
    sum = "%.5f" % sum
    return sum
