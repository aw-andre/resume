#!/usr/bin/env python3

import sys
import json
import struct
import logging
import resumecompiler
import traceback
import pathlib


SCRIPT_PATH = pathlib.Path(__file__).absolute()
SCRIPT_DIR = SCRIPT_PATH.parent

BASE_DIR = SCRIPT_DIR.parent
TEMPLATE_PATH = BASE_DIR.joinpath("resume_template.tex")
CHOICES_PATH = BASE_DIR.joinpath("choices.yaml")
DB_PATH = BASE_DIR.joinpath("resumes.db")


# Set up logging to a file
log_file = SCRIPT_DIR.joinpath("host.log")
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


def send(message: dict[str, str]) -> None:
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
            description = get_message()
            resumecompiler.compile_resume(
                description, TEMPLATE_PATH, CHOICES_PATH, DB_PATH
            )
    except Exception as e:
        logging.error("An unhandled exception occurred.")
        logging.error(traceback.format_exc())
        sys.exit(1)
