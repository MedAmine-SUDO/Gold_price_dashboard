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

    return(gold_data)


# Main loop to scrape and send messages
i = 0
try:
    while True:
        # Get gold prices
        gold_prices = get_gold_price()
        
        # Create a meaningful message value
        message_value = json.dumps(gold_prices, indent=4)  # Convert the list to a JSON string
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