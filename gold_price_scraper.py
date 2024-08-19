from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
from confluent_kafka import Producer
import time
import logging

# Configuration
kafka_host = 'localhost:9092'
topic = 'gold-topic'

# Set up logging
logging.basicConfig(level=logging.INFO)

# Create a Kafka producer instance
producer = Producer({'bootstrap.servers': kafka_host})

# Function to handle delivery reports
def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.info(f"Sent message: {msg.value().decode('utf-8')}, partition: {msg.partition()}, offset: {msg.offset()}")

# Function to extract gold prices
def get_gold_price():
    url = 'https://www.livepriceofgold.com/fr/tunisia-gold-price.html'
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        return f"Failed to retrieve data: {response.status_code}"

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract prices per gram
    gold_data = {}
    gram_section = soup.find('img', alt="Prix de l'or par gramme").find_parent('li')
    if gram_section:
        current_price = gram_section.find('span', class_='kurfiyati').get_text(strip=True)
        open_price = gram_section.find('span', class_='kurfiyati')['data-open']
        price_change = gram_section.find('b', id='GXAUUSD_CHANGE')
        price_change_percent = gram_section.find('b', id='GXAUUSD_CLASS')

        # Handle potential None values
        price_change = price_change.get_text(strip=True) if price_change else '0'
        price_change_percent = price_change_percent.get_text(strip=True) if price_change_percent else '0'

        # high_price and low_price are available in the last two bold tags
        high_price = gram_section.find_all('b')[-2].get_text(strip=True)
        low_price = gram_section.find_all('b')[-1].get_text(strip=True)
        gold_data = {
            'time': datetime.now().isoformat(),
            'category': "Prix de l'or par gramme",
            'current_price': float(current_price),
            'open_price': float(open_price),
            'price_change': float(price_change),
            'percent_change': float(price_change_percent),
            'high_price': float(high_price),
            'low_price': float(low_price)
        }
    return gold_data


# Main loop to scrape and send messages
i = 0
try:
    while True:
        # Get gold prices
        gold_price = get_gold_price()
        
        # Sérialiser le dictionnaire en JSON
        message_value = json.dumps(gold_price).encode('utf-8')  
        message_key = str(i)

        # Produce a message
        producer.produce(topic, key=message_key, value=message_value, callback=delivery_report)

        # Poll for delivery reports
        producer.poll(0)

        # Print the gold prices in a formatted string
        logging.info(f"Gold Prices List:\n{message_value}")  # Print the list in a formatted string

        i += 1
        
        time.sleep(30)

except KeyboardInterrupt:
    logging.info("Producer interrupted by user.")
finally:
    # Wait for any outstanding messages to be delivered
    producer.flush()