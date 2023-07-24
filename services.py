import datetime
import json
import sqlite3
import logging
from sqlite3 import Error

# Configuring logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_config(filepath="config.json"):
    # Load JSON configuration file
    try:
        with open(filepath) as config_file:
            config_data = json.load(config_file)
        return config_data
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from configuration file: {e}")
        return None


# function to create a database connection
def create_connection(filepath):
    connection = None
    try:
        connection = sqlite3.connect(filepath)
        logger.info(f'Successful connection with sqlite version {sqlite3.version}')
    except Error as e:
        logger.error(f"Error connecting to database: {e}")
    return connection


def get_current_time():
    # Get current date
    current_date = datetime.datetime.now()
    return current_date
