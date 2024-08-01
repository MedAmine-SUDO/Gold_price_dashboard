import requests
from bs4 import BeautifulSoup
from confluent_kafka import Producer
import json
import time

KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'gold_prices'

# Function to extract gold prices
def get_gold_price():
    url = 'https://www.livepriceofgold.com/fr/tunisia-gold-price.html'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract data for each gold price category
    gold_data = []

    # Iterate over each list item
    for li in soup.select('ul.head-ul > li'):
        category_img = li.find('img')
        if category_img:
            category = category_img.get('alt', 'Unknown category')

        current_price_span = li.select_one('.kurfiyati')
        if current_price_span:
            current_price = current_price_span.get_text(strip=True)
            open_price = current_price_span.get('data-open', 'N/A')

        price_change_span = li.select_one('[id$="_CHANGE"]')
        price_change = price_change_span.get_text(strip=True) if price_change_span else 'N/A'

        percent_change_span = li.select_one('[id$="_PERCENT"]')
        percent_change = percent_change_span.get_text(strip=True) if percent_change_span else 'N/A'

        high_low = li.select('.kurbaslik b')
        if len(high_low) == 2:
            high_price = high_low[0].get_text(strip=True)
            low_price = high_low[1].get_text(strip=True)
        else:
            high_price = low_price = 'N/A'

        gold_data.append({
            'category': category,
            'current_price': current_price,
            'open_price': open_price,
            'price_change': price_change,
            'percent_change': percent_change,
            'high_price': high_price,
            'low_price': low_price
        })

    return gold_data

# Function to publish data to Kafka
def publish_to_kafka(gold_data):
    # Initialize Kafka producer
    producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})

    try:
        producer.produce(KAFKA_TOPIC, value=json.dumps(gold_data).encode('utf-8'))
        print('published to kafka topic')
        
    except Exception as e:
        print(f"Error publishing to Kafka: {e}")


while True:
    gold_data = get_gold_price()
    print(gold_data)
    publish_to_kafka(gold_data)
    
    time.sleep(5)