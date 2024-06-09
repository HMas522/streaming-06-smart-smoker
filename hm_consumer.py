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
import os
import time
from collections import deque
import re

# Define the deques and window
smokerA_deque = deque(maxlen=5)
jackfruit_deque = deque(maxlen=20)
pineapple_deque = deque(maxlen=20)


# define a main function to run the program
def main(host: str):
    """ Continuously listen for task messages on a named queue."""
    queues = ('smokerA-queue', 'jackfruit-queue', 'pineapple-queue')
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost")
        )
    except Exception as e:
        print()
        print("ERROR: connection to RabbitMQ server failed.")
        print(f"Verify the server is running on host={host}.")
        print(f"The error says: {e}")
        print()
        sys.exit(1)
    try:
        channel = connection.channel()
        for queue in queues:
            channel.queue_delete(queue=queue)
            channel.queue_declare(queue, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume("smokerA-queue", on_message_callback=smokerA_callback, auto_ack=True)
        channel.basic_consume("jackfruit-queue", on_message_callback=jackfruit_callback, auto_ack=True)
        channel.basic_consume("pineapple-queue", on_message_callback=pineapple_callback, auto_ack=True)
        print(" [*] Waiting for messages. To exit press CTRL+C")
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

# Help with readability by adding degree sign
degree_sign = u'\N{DEGREE SIGN}'

# Define a callback function to be called when a message is received
# time sleep using "."
# Basic ack to delete from the queue once acknowledged
def smokerA_callback(ch, method, properties, body):
    """ Define behavior on getting a message."""
    print(f" [x] Received {body.decode()}")
    time.sleep(body.count(b"."))
    ch.basic_ack(delivery_tag=method.delivery_tag)

    # If not already, turn the temperatures to a float
    body_decode = body.decode('utf-8')
    temps = re.findall(r'SmokerA is (\d+\.\d+)', body_decode)
    temps_float = float(temps[0])
    smokerA_deque.append(temps_float)

    # If smoker temp decreases by 15 F or more in 2.5 min (or 5 readings)  --> smoker alert!
    if len(smokerA_deque) == smokerA_deque.maxlen:
        if smokerA_deque[0] - temps_float > 15:
            smoker_change = smokerA_deque[0] - temps_float
            print(f'''
**************************ALERT****************************
SmokerA temperature has decreased by {smoker_change}{degree_sign} in 2.5 minutes!

            ''')

# Define first food callback
def jackfruit_callback(ch, method, properties, body):
    """ Define behavior on getting a message."""
    print(f" [x] Received {body.decode()}")    
    time.sleep(body.count(b"."))
    ch.basic_ack(delivery_tag=method.delivery_tag)

    body_decode = body.decode('utf-8')
    temps = re.findall(r'Jackfruit temp is (\d+\.\d+)', body_decode)
    temps_float = float(temps[0])
    jackfruit_deque.append(temps_float)

    # If food temp change in temp is 1 F or less in 10 min (or 20 readings)  --> food stall alert!
    if len(jackfruit_deque) == jackfruit_deque.maxlen:
        if max(jackfruit_deque) - min(jackfruit_deque) < 1:
            jackfruit_change = max(jackfruit_deque) - min(jackfruit_deque)
            print(f'''
**************************ALERT****************************
Jackfruit temperature has decreased by {jackfruit_change}{degree_sign} in 10 minutes!

            ''')

# Define second food callback
def pineapple_callback(ch, method, properties, body):
    """ Define behavior on getting a message."""
    print(f" [x] Received {body.decode()}")
    time.sleep(body.count(b"."))
    ch.basic_ack(delivery_tag=method.delivery_tag)

    body_decode = body.decode('utf-8')
    temps = re.findall(r'Pineapple temp is (\d+\.\d+)', body_decode)
    temps_float = float(temps[0])
    pineapple_deque.append(temps_float)

    # If food temp change in temp is 1 F or less in 10 min (or 20 readings)  --> food stall alert!
    if len(pineapple_deque) == pineapple_deque.maxlen:
        if max(pineapple_deque) - min(pineapple_deque) < 1:
            pineapple_change = max(pineapple_deque) - min(pineapple_deque)
            print(f'''
**************************ALERT****************************
Pineapple temperature has decreased by {pineapple_change}{degree_sign} in 10 minutes!

            ''')

# ---------------------------------------------------------------------------
# If this is the script we are running, then call some functions and execute code!
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)