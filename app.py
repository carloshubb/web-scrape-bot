import os
import time
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()
# === ✅ Telegram Credentials ===
TOKEN = os.getenv("TOKEN","123456:AAFdMW5A6a2e7y3A-valFNq9VMZUbDOrG98")
LIMIT = int(os.getenv("LIMIT",'100'))
DATA_FILE = 'data/previous.json'
previous_links = []
def send_telegram_message(token, chat_id, message, photo_url):
    photo_payload = {
        'chat_id': chat_id,
        'photo': photo_url,
        'caption': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(f'https://api.telegram.org/bot{token}/sendPhoto', data=photo_payload)
        if response.status_code != 200:
            print(f"[ERROR] Telegram API response: {response.text}")
        else:
            print("📨 Telegram message sent.")
    except Exception as e:
        print(f"[EXCEPTION] Failed to send message: {e}")

def get_value_by_key(data, search_key):
    for item in data:
        if item['key'] == search_key:
            return item['value']
    return None  # if not found

def send(chat_ids, my_token):
   # chat_ids = [8008155974]
    #previous_links = load_previous_links()
    #while True:

    headers = {
        "Authorization": "www.marktplaats.nl",
        "Accept": "application/json"
    }

    offset = 0
    

    while True:
            
            api_url = f"https://www.marktplaats.nl/lrp/api/search?attributesById[]=10898&attributesById[]=473&attributesByKey[]=offeredSince%3AVandaag&l1CategoryId=91&limit={LIMIT}&offset={offset}&sortBy=SORT_INDEX&sortOrder=DECREASING&viewOptions=list-view"

            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # ✅ Assign listings to a variable
                listings = data.get("listings", [])
                if len(listings) == 0: break

                # Print each item's title
                for item in listings:
                    
                    url_path = f"https://www.marktplaats.nl{item.get("vipUrl")}"
                    if url_path in previous_links:
                        continue
                    previous_links.append(url_path)

                    description = item.get("description")
                    title = item.get("title")
                    price = item.get("priceInfo", {}).get("priceCents", 0)/100  # nested structure
                    location = item.get("location", {}).get("cityName", "")
                    image_url = item.get("pictures", [{}])[0].get("extraExtraLargeUrl", "")  
                    fuel = get_value_by_key(item.get("attributes",[{}]), "fuel")
                    transmission = get_value_by_key(item.get("attributes",[{}]), "transmission")
                    constructionYear = get_value_by_key(item.get("attributes",[{}]), "constructionYear")
                    mileage = get_value_by_key(item.get("attributes",[{}]), "mileage")
                    priorityProduct = get_value_by_key(item.get("attributes",[{}]), "priorityProduct")
                    
                    # send to telegram
                    for chat_id in chat_ids:
                        msg = (
                            f"🚗 <b>{title}</b>\n"
                            f"💰 <b>Price:</b> € {price or 'N/A'}\n"    
                            f"⛽️ {fuel}    "
                            f"⚙️ {transmission}    "
                            f"🏗️ {constructionYear}   "
                            f"📏 {mileage} km\n"
                            f"📝 <b>Description:</b>\r\n{description}\r\n"                    
                            f"📍 <b>Location:</b> {location}\r\n"                    
                            f"{f'💸 <b>{priorityProduct}</b>\r\n' if priorityProduct else ''}"                   
                            f"🔗 <b>Link:</b> <a href='{url_path}'>Open Link</a>\n"     
            
                        )
                        print(f"chat_id:{chat_id}")
                        send_telegram_message(my_token, chat_id, msg, image_url)
                        print(f"🔔 Sent Telegram alert for: {item['title']}")
            else:
                break
            
            offset += LIMIT
            # save links
            print(f"new is {offset} added")
        
        #save_links(previous_links)
    


def load_previous_links():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return set(data if isinstance(data, list) else [])
        except Exception as e:
            print(f"[ERROR] Could not read previous.json: {e}")
    return set()    

def save_links(links):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(list(links), f)


