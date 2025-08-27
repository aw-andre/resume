#!/usr/bin/env python3

import os
import sys
import json
import struct
import logging
import traceback
from typing import Any, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Set up logging to a file
log_file = os.path.join(SCRIPT_DIR, "native_host.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Native host script started.")


def get_message() -> Optional[dict[str, Any]]:
    """Read a message from stdin using Chrome native messaging protocol.

    Returns:
        Parsed JSON message as dictionary, or None if no message
    """
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        logging.info("stdin closed, exiting.")
        sys.exit(0)
    message_length = struct.unpack("@I", raw_length)[0]
    logging.info("Reading message of length: %d", message_length)
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    logging.info("Received message: %s", message)
    return json.loads(message)


def send_message(message: dict[str, Any]) -> None:
    """Send a message to the browser extension using Chrome native messaging protocol.

    Args:
        message: Dictionary to be sent as JSON message
    """
    encoded_message = json.dumps(message).encode("utf-8")
    logging.info("Sending message: %s", encoded_message)
    sys.stdout.buffer.write(struct.pack("@I", len(encoded_message)))
    sys.stdout.buffer.write(encoded_message)
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    try:
        while True:
            logging.info("Waiting for message...")
            received_message = get_message()
            if received_message is not None:
                logging.info("Processing message.")
                response = {
                    "status": "Received successfully!",
                    "original_text": received_message.get("text"),
                }
                send_message(response)
                logging.info("Response sent.")
    except Exception as e:
        logging.error("An unhandled exception occurred.")
        logging.error(traceback.format_exc())
        sys.exit(1)
