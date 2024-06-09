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
from util_logger import setup_logger

# Call setup_logger to initialize logging
logger, log_file_name = setup_logger(__file__)

#Calling a function to ask the user if they want to see the Admin Webpage of RabbitMQ.
def offer_rabbitmq_admin_site(show_offer=True):
    """Offer to open the RabbitMQ Admin website"""
    if show_offer:
        ans = input("Would you like to monitor RabbitMQ queues? y or n ")
        print()
        if ans.lower() == "y":
            webbrowser.open_new("http://localhost:15672/#/queues")
            print()

def send_temps(host: str, queue_name: str):
    """
    Creates and sends a message to the queue each execution.
    This process runs and finishes.

    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        queue_name (str): the name of the queue
    """
    try:
        # create a blocking connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        # use the connection to create a communication channel
        ch = conn.channel()
        # use the channel to declare a durable queue
        # a durable queue will survive a RabbitMQ server restart
        # and help ensure messages are processed in order
        # messages will not be deleted until the consumer acknowledges
        
        ch.queue_declare(queue="smokerA", durable=True)
        ch.queue_declare(queue="jackfruit", durable=True)
        ch.queue_declare(queue="pineapple", durable=True)

        with open('smoker-temps.csv', 'r') as file:
            reader = csv.reader(file, delimiter=",")
            for row in reader:
                Time,Channel1,Channel2,Channel3 = row
                
                if Channel1: 
                    smoker_temp = ','.join([Time, Channel1])
                    ch.basic_publish(exchange="", routing_key="smokerA", body=smoker_temp)
                    logger.info(f" [*] Smoker Temp is {smoker_temp}")
                
                if Channel2:
                    jackfruit = ','.join([Time, Channel2])
                    ch.basic_publish(exchange="", routing_key="jackfruit", body=jackfruit)
                    logger.info(f" [*] Jackfruit Temp is {jackfruit}")

                if Channel3:
                    pineapple = ','.join([Time, Channel3])
                    ch.basic_publish(exchange="", routing_key="pineapple", body=pineapple)
                    logger.info(f" [*] Pineapple Temp is {pineapple}")

    except pika.exceptions.AMQPConnectionError as e:
        logger.info(f"Error: Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
       

        # close the connection to the server
        conn.close()

# Standard Python idiom to indicate main program entry point
# This allows us to import this module and use its functions
# without executing the code below.
# If this is the program being run, then execute the code below
if __name__ == "__main__":  
    # ask the user if they'd like to open the RabbitMQ Admin site
    offer_rabbitmq_admin_site() 

    # send the message to the queue
    send_temps("localhost","smokerA")
    send_temps("localhost","jackfruit")
    send_temps("localhost","pineapple")