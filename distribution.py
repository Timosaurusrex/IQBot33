import time
import requests
from telegram import *
import sys

save_trend = 0

def telegram():
    global last_date
    message = check_for_message().lower()

    if message == "//kill":
        send_message("Good buy Motherfucker <3")
        sys.exit(0)

def coins_distribution():
    global save_trend

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
                print("Over 10%: " + symbol.upper())
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

    print(points)
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

    with open("distribution.txt", "r+") as f:
        if points == 2 or points == 1:#not (points == 1 and save_trend != 2) or :
            f.write(str(1))
            print(f"Derzeitige Markt: up {points}")
        else:
            f.write(str(0))
            print(f"Derzeitige Markt: down {points}")

    if points != save_trend:
        save_trend = points

if __name__ == '__main__':

    while True:
        telegram()

        start = time.time()
        coins_distribution()
        ende = time.time()
        print('{:5.3f}s'.format(ende - start))