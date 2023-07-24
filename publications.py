import requests
import sqlite3
import ast
import logging
from services import get_config, get_current_time

# Configuring logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Getting application configuration
config = get_config()


# Articles search via API
def search_medium_articles(ap_config):
    try:
        # Extracting Search URL from configuration
        url = ap_config["data_sources"]["medium"][0]["search_url"]
        querystring = {"query": ap_config["application"]["topic"]}
        headers = {
            "X-RapidAPI-Key": ap_config["data_sources"]["medium"][0]["headers"]["X-RapidAPI-Key"],
            "X-RapidAPI-Host": ap_config["data_sources"]["medium"][0]["headers"]["X-RapidAPI-Host"]
        }

        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    except requests.exceptions.HTTPError as errh:
        logger.error(f"HTTP Error: {errh}")
        return None
    except requests.exceptions.ConnectionError as errc:
        logger.error(f"Error Connecting: {errc}")
        return None
    except requests.exceptions.Timeout as errt:
        logger.error(f"Timeout Error: {errt}")
        return None
    except requests.exceptions.RequestException as err:
        logger.error(f"Something went wrong with the request: {err}")
        return None


# Store articles id in database
def db_insert_article_id(content):
    # Setting up db location variable
    db_path = config["db"]["path"]

    # Get current date
    current_date = get_current_time()

    # Establish a connection to the database
    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            # Assemble insert payload
            insert_data = [(str(current_date), str(content))]
            # Insert payload into database
            cursor.executemany("INSERT INTO raw_medium_articles VALUES(?,?)", insert_data)
            connection.commit()
            logger.info("Data inserted successfully")

    except sqlite3.Error as error:
        logger.error(f"Failed to insert data into sqlite table: {error}")


# Read all raw data rows from the database
def db_get_all_articles():
    # Setting db location variable
    db_path = config["db"]["path"]

    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            # Query all data from database
            cursor.execute("SELECT * FROM raw_medium_articles")
            fetch_data = cursor.fetchall()
            return fetch_data

    except sqlite3.Error as error:
        logger.error(f"Failed to read data from sqlite table: {error}")
        return None


# Fetches the latest payload data from the database
def db_get_latest_publications():
    # Setting db location variable
    db_path = config["db"]["path"]

    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            # Query data from database
            cursor.execute("SELECT MAX(timestamp) as timestamp, payload FROM raw_medium_articles")
            fetch_data = cursor.fetchall()

            articles_dump = fetch_data[0][1]  # Extract payload from fetch_data
            articles_dump = ast.literal_eval(articles_dump)  # Convert to Python dictionary
            articles_dump = articles_dump['articles']  # Extract articles list from dictionary
            return articles_dump

    except sqlite3.Error as error:
        logger.error(f"Failed to read data from sqlite table: {error}")
        return None


if __name__ == '__main__':
    logger.info("Running publications module ...")
    dump = search_medium_articles(config)
    if dump is not None:
        db_insert_article_id(dump)
        dump_api_list = db_get_all_articles()
        logger.info(f"A list of articles received from API: {dump_api_list}")
