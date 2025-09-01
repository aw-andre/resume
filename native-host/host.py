#!/usr/bin/env python3

import os
import sys
import json
import struct
import logging
import traceback
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Set up logging to a file
log_file = os.path.join(SCRIPT_DIR, "host.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def receive() -> str:
    """
    Read a message from stdin using Chrome native messaging protocol.

    Returns:
        text from received message
    """
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        logging.info("stdin closed, exiting.")
        sys.exit(0)

    message_length = struct.unpack("@I", raw_length)[0]
    logging.info("Reading message of length: %d", message_length)

    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    logging.info("Received message: %s", message)

    json_message = json.loads(message)
    if json_message is None:
        return ""
    return json_message.get("text", "")


def send(message: dict[str, Any]) -> None:
    """
    Send a message to the browser extension using Chrome native messaging protocol.

    Args:
        message: dictionary to be sent as JSON
    """
    encoded_message = json.dumps(message).encode("utf-8")
    logging.info("Sending message: %s", encoded_message)
    sys.stdout.buffer.write(struct.pack("@I", len(encoded_message)))
    sys.stdout.buffer.write(encoded_message)
    sys.stdout.buffer.flush()


def get_message() -> str:
    """
    Read a message via Chrome native messaging and respond to the browser.

    Returns:
        text from received message
    """
    message = receive()
    send({"status": "Received successfully!", "original_text": message})
    return message


if __name__ == "__main__":
    logging.info("Native host script started.")

    try:
        while True:
            get_message()
    except Exception as e:
        logging.error("An unhandled exception occurred.")
        logging.error(traceback.format_exc())
        sys.exit(1)
