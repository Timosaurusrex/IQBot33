import requests
import json

key = "bot2132832222:AAFvYlCTi55lsTG_clJs1zwnlX_2kjjsat0"
const_chat_id = "1057027063"

def send_message(message, chat_id = const_chat_id):
    #x = requests.get('https://api.telegram.org/' + key + '/sendMessage?chat_id=' + str(chat_id) + '&text=' + str(message)) #Without buttons
    x = requests.get('https://api.telegram.org/' + key + '/sendMessage?chat_id=' + str(chat_id) + '&text=' + str(message) + '&reply_markup={"keyboard":[["/wallet"],["/history"],["/end"],["/help"]]}') #with buttons
    if x.text[2] == 'o' and x.text[3] == 'k':
        return 200
    else:
        return 0

def check_for_message():
    x = requests.get("https://api.telegram.org/" + key + "/getUpdates")
    y = json.loads(x.text)
    return y["result"][len(y["result"]) - 1]["message"]["text"]

def check_for_message_date():
    x = requests.get("https://api.telegram.org/" + str(key) +"/getUpdates")
    y = json.loads(x.text)
    return y["result"][len(y["result"]) - 1]["message"]["date"]
