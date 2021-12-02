#Geschrieben von Christoph Handschuh, am 1.10.2021
#Simuliert einen Crypto-Broker
#Quantity added by Timo Perzi

import requests
import json

startcapital = 100
fee = 0.025

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
            f = open("coins/" + symbol.upper() + ".txt", "r")
            oldquantity = float(f.read())
            f.close()
        except IOError:
            f = open("coins/" + symbol.upper() + ".txt", "w")
            f.write("0")
            f.close()
            oldquantity = 0
        fee = ((quantity * symbolprice)/100) * fee
        #print(fee)
        f = open("coins/" +symbol.upper() + ".txt", "w")
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
    f = open("coins/" + symbol.upper() + ".txt", "r")
    crypto = float(f.read())
    f.close()
    if quantity > crypto:
        return "You are broke"
    else:
        symbolprice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + symbol.upper())
        symbolprice = json.loads(symbolprice.text)
        symbolprice = float(symbolprice["price"])
        usdtcurrent = symbolprice*quantity
        f = open("coins/" + symbol.upper() + ".txt", "w")
        f.write(str(crypto - quantity))
        f.close()
        f = open("USDT.txt", "r")
        usdt = float(f.read())
        f.close()
        f = open("USDT.txt", "w")
        f.write(str(usdt + usdtcurrent))
        f.close()
        return 200

def sell_all(symbol):
    f = open("coins/" + symbol.upper() + ".txt", "r")
    crypto = float(f.read())
    f.close()
    symbolprice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + symbol.upper()).json()
    symbolprice = float(symbolprice["price"])
    f = open("coins/" + symbol.upper() + ".txt", "w")
    f.write("0")
    f.close()
    f = open("USDT.txt", "r")
    usdt = float(f.read())
    f.close()
    f = open("USDT.txt", "w")
    f.write(str(usdt + (symbolprice * crypto)))
    f.close()
    return 200


def Quantity(symbol, mtg):
    symbolprice = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + symbol.upper())
    symbolprice = json.loads(symbolprice.text)
    symbolprice = float(symbolprice["price"])
    f = open("USDT.txt", "r")
    money = float(f.read())
    f.close()
    money = money/mtg
    #print(money/(symbolprice * 1.05))
    return (money * 0.99)/symbolprice