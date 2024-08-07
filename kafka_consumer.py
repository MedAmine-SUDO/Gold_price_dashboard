from confluent_kafka import Consumer, KafkaError
import time
from datetime import datetime
import random

# Configuration
kafka_host = 'localhost:9092'
topic = 'gold-topic'  # Ensure this matches the producer's topic
group_name = 'consumer-group1'

# Consumer configuration
conf = {
    'bootstrap.servers': kafka_host,
    'group.id': group_name,
    'auto.offset.reset': 'earliest'  # Start reading at the earliest message
}

# Create a Kafka consumer instance
consumer = Consumer(conf)

# Subscribe to the topic
consumer.subscribe([topic])

print(f"Listening to topic {topic}...")

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
        current_time = datetime.now().strftime('%S:%f')[:-3]  # Get seconds and milliseconds

        # Process the message
        message_value = msg.value().decode('utf-8')
        print(f"Consumed message: {message_value} partition {msg.partition()} at {current_time}")
        
        # Optional: Parse the message if needed
        # For example, if you want to extract specific fields from the message
        # You can split the message or use JSON parsing if the message is in JSON format

        time.sleep(random.randint(0, 100) / 1000.0)  # Sleep for a random time between 0 and 100 milliseconds

except KeyboardInterrupt:
    print("Consumer interrupted by user.")

finally:
    # Close the consumer
    consumer.close()