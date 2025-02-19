import pandas as pd
import requests
from price_parser import Price
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
PRODUCT_URL_CSV= "products.csv"
SAVE_TO_CSV= True
PRICES_CSV = "prices.csv"
SEND_MAIL = True

def bot_send_text(df):
    for _, product in df.iterrows():  # Iterate over rows properly
        message = f"{product['product']} ha bajado a {product['price']} €"
        send_text = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={bot_chat_id}&text={message}"    
        requests.get(send_text)
    return True

def get_urls(csv_file):
    df= pd.read_csv(csv_file)
    return df

def get_response(url):
    driver.get(url)
    driver.implicitly_wait(10)
    return driver.page_source

def get_price(html):
    el = driver.find_element(By.CLASS_NAME, "product-info__price-major")
    price = Price.fromstring(el.text.strip())
    return price.amount_float

def process_products(df):
    updated_products= []
    for product in df.to_dict("records"):
        html = get_response(product["url"])
        product["price"] = get_price(html)
        product["alert"] = product["price"] < product["alert_price"]
        updated_products.append(product)
    return pd.DataFrame(updated_products)
    
def get_mail(df):
    subject = "Atenció potxola el preu ha baixat"
    body = df[df["alert"]].to_string()
    subject_and_message= f"Subject:{subject}\n\n{body}"
    return subject_and_message

def send_mail(df):
    message_text = get_mail(df)
    if not message_text:
        print("No price drops, skipping email.")
        return

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(mail_user, mail_pass)
        smtp.sendmail(mail_user, mail_to, message_text)

def main():
    df = get_urls(PRODUCT_URL_CSV)
    print(df)
    df_updated = process_products(df)
    if SAVE_TO_CSV:
        df_updated.to_csv(PRICES_CSV, index=False, mode="a")
        print("saved")
    if SEND_MAIL:
        bot_send_text(df_updated)
        print("sended")

main()