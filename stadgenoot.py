#!/usr/bin/python3
import sys
import json
import os
import atexit
from tkinter import S
import requests
import time
from telethon import TelegramClient

seen_listings = []

# TELEGRAM
# create bot by talking to botfather http://t.me/BotFather
# and get your api_id, api_hash, token
# set username and start a chat to allow messages
username = '...'
api_id = ''
api_hash = ''
bot_token = ''

# We have to manually call "start" if we want an explicit bot token
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

def exit_handler():
    print(seen_listings)
    filename = "./runs/listings_"+str(int(time.time()))+".json"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w+') as f:
        f.write(json.dumps(seen_listings))

async def message(message):
    await client.send_message(username, str(message))

async def listing(message):
    await client.send_message(username, 
    'New listing found: ' + str(message['Title']) + ' - https://aanbod.stadgenoot.nl/' + str(message["Id"]) + ' - Price: ' + str(message["Price"]),
        link_preview=True
    )

async def main(argv):
    try:
        if argv[0]:
            print("trying import of: " + str(argv[0]))
            with open(argv[0], 'r') as f:
                for item in json.loads(f.read()):
                    seen_listings.append(item)
            print("listings added: " + str(seen_listings))
    except:
        print("No file or failed import, starting blank")
        print("Usage: python3 stadgenoot.py ids.json")

    print("starting")
    while True:
        url = 'https://aanbod.stadgenoot.nl/umbraco/WebCit/AanbodApi/GetAanbod?'+str(int(time.time()))+'&init=true&type=wonen&page=1&orderType=date&order=desc&filters=rentOrSale;Huur'
        response = requests.get(url)
        new_count = 0
        for item in response.json()["Items"]:
            if item["Id"] not in seen_listings:
                # new listing
                print(str(new_count) + " new listings found - https://aanbod.stadgenoot.nl/" + str(item["Id"]))
                new_count = new_count + 1
                await listing(item)
                seen_listings.append(item["Id"])
        time.sleep(10)
atexit.register(exit_handler)
if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main(sys.argv[1:]))
