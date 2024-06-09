"""
Student: Hayley M
Date: 08Jun24

Message listener 

Description:
This script continuously listens for messages on a named queue.
This terminal must be open and dedicated to this process. 
(If you want to emit messages, open a different terminal window.)

Remember:
- Use Control + C to close a terminal and end the listening process.
- Use the up arrow to recall the last command executed in the terminal.
"""
# Basic imports to run code
import pika
import sys
import time
import struct
from datetime import datetime
from collections import deque

# Define the deques and window
smokerA_deque = deque(maxlen=5)
jackfruit_deque = deque(maxlen=20)
pineapple_deque = deque(maxlen=20)

# Define smokerA call back
# Use deque/window to append temperature to the limit set
def smokerA_callback(ch, method, properties, body):
    timestamp, temperature = struct.unpack('!df', body)
    timestamp_str = datetime.fromtimestamp(timestamp).strftime("%m/%d/%y %H:%M:%S")
    print(f" [x] Received from smoker queue: {timestamp_str} - Temperature: {temperature}F")

    smokerA_deque.append(temperature)

    if len(smokerA_deque) == smokerA_deque.maxlen:
        if smokerA_deque[0] - temperature >= 15:
            print(" [!] Smoker temp decreases by 15 F or more in 2.5 min (or 5 readings)  --> smoker alert!")

    print(" [x] Done.")
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Define first food callback
def jackfruit_callback(ch, method, properties, body):
    timestamp, temperature = struct.unpack('!df', body)
    timestamp_str = datetime.fromtimestamp(timestamp).strftime("%m/%d/%y %H:%M:%S")
    print(f" [*] Received from food A queue: {timestamp_str} - Temperature: {temperature}F")

    jackfruit_deque.append(temperature)

    if len(jackfruit_deque) == jackfruit_deque.maxlen:
        if max(jackfruit_deque) - min(jackfruit_deque) <= 1:
            print(" [!] Food temp change in temp is 1 F or less in 10 min (or 20 readings)  --> food stall alert!")

    print(" [x] Done.")
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Define second food callback
def pineapple_callback(ch, method, properties, body):
    timestamp, temperature = struct.unpack('!df', body)
    timestamp_str = datetime.fromtimestamp(timestamp).strftime("%m/%d/%y %H:%M:%S")
    print(f" [*] Received from food B queue: {timestamp_str} - Temperature: {temperature}F")

    pineapple_deque.append(temperature)

    if len(pineapple_deque) == pineapple_deque.maxlen:
        if max(pineapple_deque) - min(pineapple_deque) <= 1:
            print(" [!] Food temp change in temp is 1 F or less in 10 min (or 20 readings)  --> food stall alert!")

    print(" [x] Done.")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    """Continuously listen for task messages on named queues."""
    hn = "localhost"

    try:
        # Create a blocking connection to the RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hn))
    except Exception as e:
        print()
        print("ERROR: connection to RabbitMQ server failed.")
        print(f"Verify the server is running on host={hn}.")
        print(f"The error says: {e}")
        print()
        sys.exit(1)

    try:
        # Use the connection to create a communication channel
        channel = connection.channel()

        # Declare each queue
        queues = ["smokerA", "jackfruit", "pineapple"]
        for queue in queues:
            channel.queue_delete(queue=queue)
            channel.queue_declare(queue=queue, durable=True)

        # Set the prefetch count to limit the number of messages being processed concurrently
        channel.basic_qos(prefetch_count=1)

        # Configure the channel to listen on each queue with corresponding callback function
        channel.basic_consume(queue="smokerA", on_message_callback=smokerA_callback, auto_ack=False)
        channel.basic_consume(queue="jackfruit", on_message_callback=jackfruit_callback, auto_ack=False)
        channel.basic_consume(queue="pineapple", on_message_callback=pineapple_callback, auto_ack=False)

        # Print a message to the console for the user
        print(" [*] Waiting for messages. To exit press CTRL+C")

        # Start consuming messages via the communication channel
        channel.start_consuming()

    except Exception as e:
        print()
        print("ERROR: something went wrong.")
        print(f"The error says: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        print(" User interrupted continuous listening process.")
        sys.exit(0)
    finally:
        print("\nClosing connection. Goodbye.\n")
        connection.close()

if __name__ == "__main__":
    main()