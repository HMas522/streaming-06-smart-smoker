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

import sys
import pika
import csv
import time
import webbrowser
import logging
from collections import deque
import re

from util_logger import setup_logger
logger, logname = setup_logger(__file__)

# Define the deques outside of functions so they can be appended to
smoker_deque = deque(maxlen=5)
foodA_deque = deque(maxlen=20)
foodB_deque = deque(maxlen=20)

def process_message(ch, method, properties, body):
    """
    Callback function to process a received message.
    The signature of this function is defined by the Pika library.

    Parameters:
    - ch: The channel object from RabbitMQ. It provides methods to interact with the protocol,
          but we don't need them in this particular callback.
    - method: Contains details about the delivery method and its properties,
              such as the delivery tag or the exchange/routing key.
              We don't use it in this example.
    - properties: Message properties like content_type or delivery_mode.
                  Not used here since we're focused on the message body.
    - body: The body of the message (the actual content).
    """
    logger.info(f"Received: {body.decode()}")


# define a main function to run the program
# pass in the hostname as a string parameter if you like
# if no argument is provided, set a default value to localhost
def main(hn: str = "localhost"):
    """Main program entry point."""

    # when a statement can go wrong, use a try-except block
    try:
        # try this code, if it works, keep going
        # create a blocking connection to the RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hn))

    # except, if there's an error, do this
    except Exception as e:
        logger.error()
        logger.error("ERROR: connection to RabbitMQ server failed.")
        logger.error(f"Verify the server is running on host={hn}.")
        logger.error(f"The error says: {e}")
        logger.error()
        sys.exit(1)

    try:
        # use the connection to create a communication channel
        channel = connection.channel()

        # use the channel to declare a queue
        channel.queue_declare(queue="hello")

        # use the channel to consume messages from the queue
        # on getting a message, execute the login in the callback function
        channel.basic_consume(
            queue="hello", on_message_callback=process_message, auto_ack=True
        )

        # print a message to the console for the user
        logger.info(" [*] Waiting for messages. To exit press CTRL+C")

        # start consuming messages via the communication channel
        channel.start_consuming()

    # except, in the event of an error OR user stops the process, do this
    except Exception as e:
        logger.error(
            "ERROR: An issue occurred while setting up or listening for messages."
        )
        logger.error(f"Error Details: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("User interrupted the listening process.")
        sys.exit(0)
    finally:
        logger.info("Closing connection. Goodbye.")
        connection.close()


# ---------------------------------------------------------------------------
# If this is the script we are running, then call some functions and execute code!
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
