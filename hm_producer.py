"""
Student: Hayley M
Date: 01Jun24

Message sender / emitter /producer

Description:
Create channels or 3 different queues for our temperatures for each producer that creates a temperature.

"""
# Imports from standard Library

import csv
import pika
import sys
import webbrowser
import pathlib
import time
import struct
from datetime import datetime
from util_logger import setup_logger

# Call setup_logger to initialize logging
logger, log_file_name = setup_logger(__file__)

def offer_rabbitmq_admin_site():
    """Offer to open the RabbitMQ Admin website"""
    ans = input("Would you like to monitor RabbitMQ queues? y or n ")
    print()
    if ans.lower() == "y":
        webbrowser.open_new("http://localhost:15672/#/queues")
        print()

def connect_rabbitmq():
    """Connect to RabbitMQ server and return the connection and channel"""
    try:
        # Create a blocking connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        # Use the connection to create a communication channel
        ch = conn.channel()

        # Define queues
        # Define delete queue in channel
        # Define declare in channel
        queues = ["smokerA", "jackfruit", "pineapple"]
        for queue_name in queues:
            ch.queue_delete(queue=queue_name)
            ch.queue_declare(queue=queue_name, durable=True)

        return conn, ch
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Error: Connection to RabbitMQ server failed: {e}")
        sys.exit(1)

def send_message(host: str, queue_name: str, message: str):
    """
    Creates and sends a message to the queue each execution.
    This process runs and finishes.

    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        queue_name (str): the name of the queue
        message (str): the message to be sent to the queue
    """
    try:
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        ch = conn.channel()
        ch.queue_declare(queue=queue_name, durable=True)
        ch.basic_publish(exchange="", routing_key=queue_name, body=message)
        print(f"{message}")
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error: Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
        conn.close()

# Define how the csv will be read by RabbitMQ
# data_row tells us how the code will read the columns in our csv
# Column 0 is our time stamp 
# Column 1 is our smoker temp
# Columnn 2 is food A
# Column 3  is food B

def process_csv():
    """Reads data from CSV file and sends it to RabbitMQ queues."""
    with open("smoker-temps.csv", newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        
        for data_row in reader:
            time_stamp_str = data_row[0]
            smokerA_temp_str = data_row[1]
            jackfruit_temp_str = data_row[2]
            pineapple_temp_str = data_row[3]

             # Convert timestamp string to Unix timestamp (float)
            timestamp = datetime.strptime(time_stamp_str, "%m/%d/%y %H:%M:%S").timestamp()

            if smokerA_temp_str:
                message = struct.pack('!df', timestamp, float(smokerA_temp_str))
                send_message("localhost", "smokerA", message)
            
            if jackfruit_temp_str:
                message = struct.pack('!df', timestamp, float(jackfruit_temp_str))
                send_message("localhost", "jackfruit", message)
            
            if pineapple_temp_str:
                message = struct.pack('!df', timestamp, float(pineapple_temp_str))
                send_message("localhost", "pineapple", message)

if __name__ == "__main__":
    offer_rabbitmq_admin_site()
    process_csv()

    host = 'localhost'
    