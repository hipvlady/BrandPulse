import requests
import datetime
import sqlite3
import logging
from dateutil.relativedelta import relativedelta
from services import get_config, get_current_time
from publications import db_get_latest_publications

# Configuring logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Getting application configuration
config = get_config()
API_LIMIT = config["data_sources"]["medium"][0]["publications_limit"]


def get_article_metadata(app_config, article_id):
    try:
        # Assembling URL from configuration
        url = f'{app_config["data_sources"]["medium"][0]["article_info"]}' + f'{article_id}'
        headers = {
            "X-RapidAPI-Key": f'{app_config["data_sources"]["medium"][0]["headers"]["X-RapidAPI-Key"]}',
            "X-RapidAPI-Host": f'{app_config["data_sources"]["medium"][0]["headers"]["X-RapidAPI-Host"]}'
        }

        response = requests.get(url, headers=headers)
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


def db_read_metadata_id():
    # Setting up db location variable
    db_path = config["db"]["path"]

    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            # Query data from database
            cursor.execute("SELECT id FROM events")
            fetch_data = cursor.fetchall()
            return fetch_data

    except sqlite3.Error as error:
        logger.error(f"Failed to read data from sqlite table: {error}")
        return None


def db_get_metadata_id(item_id):
    # Setting up db location variable
    db_path = config["db"]["path"]

    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            # Query the database
            cursor.execute(f"SELECT id FROM events WHERE id=\'{item_id}\'")
            fetch_data = cursor.fetchall()
            return fetch_data if fetch_data else None

    except sqlite3.Error as error:
        logger.error(f"Failed to read data from sqlite table: {error}")
        return None


def db_insert_metadata(metadata):
    # Setting up db location variable
    db_path = config["db"]["path"]

    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            # Insert the event into the database
            insert_data = [(metadata['id'],
                            metadata['published_at'],
                            ','.join(metadata['tags']),
                            metadata['url'],
                            metadata['lang'],
                            metadata['publication_id'],
                            metadata['title'],
                            metadata['voters'],
                            None,
                            None)]
            cursor.executemany("INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?,?)", insert_data)
            connection.commit()
            logger.info(f'record inserted successfully with id {metadata["id"]}')

    except sqlite3.Error as error:
        logger.error(f"Failed to insert data into sqlite table: {error}")


def metadata_process(metadata):
    # Setting up db location variable
    db_path = config["db"]["path"]

    # Get current date
    current_date = get_current_time()

    # Get the date for 3 months ago
    to_date = current_date - relativedelta(months=6)

    try:
        # Convert string to datetime object
        published_date = datetime.datetime.strptime(metadata['published_at'], "%Y-%m-%d %H:%M:%S")

        if published_date > to_date:
            with sqlite3.connect(db_path) as connection:
                db_insert_metadata(metadata)

    except ValueError as error:
        logger.error(f"Error parsing the date string. Please ensure it's in the correct format. "
                     f"Error details: {error}")
    except KeyError as error:
        logger.error(f"Error accessing keys in metadata. Please ensure the dictionary has the "
                     f"correct keys. Error details: {error}")


def db_get_not_processed_id():
    # Getting the latest publications ids
    fetched_data = db_get_latest_publications()
    sql_dump = tuple(fetched_data)

    # Setting up db location variable
    db_path = config["db"]["path"]

    try:
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()

            # Query the database to select IDs that do not exist in table ABC
            cursor.execute("SELECT id FROM events WHERE id NOT IN ({})".format(','.join(['?'] * len(sql_dump))),
                           sql_dump)
            rows = cursor.fetchall()

            # Convert the result to a list of IDs
            existing_ids = [row[0] for row in rows]

            # IDs that are not in table
            ids_not_in_table = [item for item in sql_dump if item not in existing_ids]
            return ids_not_in_table

    except sqlite3.Error as error:
        logger.error(f"Failed to read data from sqlite table: {error}")
        return None


if __name__ == "__main__":
    logger.info("Running metadata process module ...")
    id_to_query = db_get_not_processed_id()
    if id_to_query is not None:
        for item in id_to_query:
            for i in range(API_LIMIT):
                metadata = get_article_metadata(config, item)
                if metadata is not None:
                    metadata_process(metadata)
