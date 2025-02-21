import pandas as pd
import requests
from price_parser import Price
import json
PRODUCT_URL_CSV= "products.csv"
SAVE_TO_CSV= True
PRICES_CSV = "prices.csv"
SEND_MAIL = True

def bot_send_text(df):
    for _, product in df.iterrows():
        if product['alert']:  # Only send if the price has dropped
            message = f"{product['product']} ha bajado a {product['price']} €"
            send_text = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={bot_chat_id}&text={message}"
            requests.get(send_text)
    return True


def get_urls(csv_file):
    return pd.read_csv(csv_file)


def get_response(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def get_price(product):
    try:
        return product['prices'][2]['price']
    except (IndexError, TypeError, KeyError):
        print("Error extracting price")
        return None


def process_products(df):
    updated_products = []
    
    for product in df.to_dict("records"):
        product_data = get_response(product["url"])
        
        if product_data:
            new_price = get_price(product_data)
            if new_price is not None:
                product["price"] = new_price
                product["alert"] = new_price < product["alert_price"]
        
        updated_products.append(product)
    
    return pd.DataFrame(updated_products)


def main():
    df = get_urls(PRODUCT_URL_CSV)
    df_updated = process_products(df)

    # Save updated prices back to products.csv to keep track of latest prices
    df_updated.to_csv(PRODUCT_URL_CSV, index=False, mode="w")

    # Save price records separately to prices.csv
    if SAVE_TO_CSV:
        df_updated.to_csv(PRICES_CSV, index=False, mode="w")
        print("Prices updated in CSV.")

    # Send Telegram notification if price has dropped
    if SEND_MAIL:
        bot_send_text(df_updated)
        print("sended")

main()