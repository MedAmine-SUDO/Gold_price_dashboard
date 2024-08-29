from confluent_kafka import Consumer, KafkaError
import time
from datetime import datetime
import random
import psycopg2
import json

import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Configuration
kafka_host = os.getenv('KAFKA_HOST')
topic = os.getenv('KAFKA_TOPIC')  
group_name = 'consumer-group1'

# TimescaleDB configuration
db_host = os.getenv('KAFKA_HOST')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT')

# Consumer configuration
conf = {
    'bootstrap.servers': kafka_host,
    'group.id': group_name,
    'auto.offset.reset': 'earliest'  
}

# Create a Kafka consumer instance
consumer = Consumer(conf)

# Subscribe to the topic
consumer.subscribe([topic])

print(f"Listening to topic {topic}...")

# Connect to TimescaleDB
try:
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port= db_port
    )
    cursor = conn.cursor()
    print("Connected to TimescaleDB.")
except Exception as e:
    print(f"Error connecting to TimescaleDB: {e}")
    exit(1)

try:
    while True:
        # Poll for new messages
        msg = consumer.poll(10.0)  # Wait for up to 10 seconds for a message
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                continue
            else:
                print(f"Error consuming: {msg.error()}")
                break

        # Get current time formatted as seconds and milliseconds
        current_time = datetime.now()  

        # Process the message
        message_value = msg.value().decode('utf-8')
        print(f"Consumed message: {message_value} partition {msg.partition()} at {current_time}")

        # Parse the JSON message
        data = json.loads(message_value)

        # Insérer le message dans TimescaleDB
        try:
            insert_query = """INSERT INTO gold_prices (time, category, current_price, open_price, price_change, percent_change, high_price, low_price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""                  
            cursor.execute(insert_query, (
                data['time'],  
                data['category'],
                data['current_price'],  
                data['open_price'],      
                data['price_change'],
                data['percent_change'],             
                data['high_price'],       
                data['low_price']         
            ))
            conn.commit()  
            print("Inserted message into TimescaleDB.")
        except Exception as e:
            print(f"Error inserting into TimescaleDB: {e}")
            print(f"SQL Query: {insert_query}") 
            conn.rollback()  
        
        

        time.sleep(random.randint(0, 100) / 1000.0)  

except KeyboardInterrupt:
    print("Consumer interrupted by user.")

finally:
    # Close the consumer and database connection
    consumer.close()
    cursor.close()
    conn.close()
    print("Consumer and database connection closed.")