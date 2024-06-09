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

def send_message(host: str, queue_name: str, message: bytes):
    """
    Creates and sends a binary message to the specified queue.

    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        queue_name (str): the name of the queue
        message (bytes): the binary message to be sent to the queue
    """

    try:
        # create a blocking connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        # use the connection to create a communication channel
        ch = conn.channel()
        # use the channel to declare a durable queue
        ch.queue_declare(queue=queue_name, durable=True)
        # use the channel to publish a message to the queue
        ch.basic_publish(exchange="", routing_key=queue_name, body=message)
        # print a message to the console for the user
        print(f" [x] Sent message to {queue_name}")
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error: Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
        # close the connection to the server
        conn.close()

# Define how the csv will be read by RabbitMQ
# data_row tells us how the code will read the columns in our csv
# Column 0 is our time stamp 
# Column 1 & Channel 1 is our smoker temp
# Columnn 2 & Channel 2 is food A
# Column 3 & Channel 3 is food B

def process_csv():
    """Process the CSV file and send messages to RabbitMQ queues"""
    try:
        csv_file_path = "C:\\Users\\Hayley\\Documents\\streaming-05-smart-smoker\\smoker-temps.csv"
        with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)  
            
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

    # Error handling
    except FileNotFoundError:
        logger.error("CSV file not found.")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Error processing CSV: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    offer_rabbitmq_admin_site()
    process_csv()