from confluent_kafka import Consumer, KafkaException
import json

# Configuration for the Kafka consumer
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'gold_price_consumer',  
    'auto.offset.reset': 'earliest', 
    'enable.auto.commit': True  
}

# Initialize Kafka consumer
consumer = Consumer(conf)

# Subscribe to the 'gold_price' topic
consumer.subscribe(['gold-price'])

try:
    while True:
        # Poll for a message
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue  

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print('%% %s [%d] reached end at offset %d\n' % (msg.topic(), msg.partition(), msg.offset()))
            else:
                # Handle other Kafka errors
                print(f"Kafka error: {msg.error()}")
                continue
        else:
            # Message received successfully
            gold_data = json.loads(msg.value().decode('utf-8'))
            print("Received gold price data:")
            for item in gold_data:
                print(f"Category: {item['category']}")
                print(f"Current Price: {item['current_price']}")
                print(f"Open Price: {item['open_price']}")
                print(f"Price Change: {item['price_change']}")
                print(f"Percent Change: {item['percent_change']}")
                print(f"High Price: {item['high_price']}")
                print(f"Low Price: {item['low_price']}")
except KeyboardInterrupt:
    pass
finally:
    # Close the consumer on exit
    consumer.close()                