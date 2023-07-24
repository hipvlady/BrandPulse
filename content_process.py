import requests
import logging
from nltk.sentiment import SentimentIntensityAnalyzer
from services import get_config, create_connection, get_current_time
from metadata_process import db_read_metadata_id

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

config = get_config()
# Setting up db location variable
db_path = config["db"]["path"]
API_LIMIT = config["data_sources"]["medium"][0]["publications_limit"]


def get_content(app_config, article_id):
    # Assembling URL from configuration
    url = f'{app_config["data_sources"]["medium"][0]["content_url"]}{article_id}/content'
    headers = {
        "X-RapidAPI-Key": app_config["data_sources"]["medium"][0]["headers"]["X-RapidAPI-Key"],
        "X-RapidAPI-Host": app_config["data_sources"]["medium"][0]["headers"]["X-RapidAPI-Host"]
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for unsuccessful HTTP responses
        content = response.json()

        # Check if "content" key exists in the response
        if "content" in content:
            return {"id": article_id, "content": content["content"]}
        else:
            logging.error(f"'content' not found in the response for article_id: {article_id}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching content for article_id: {article_id}. Exception: {e}")
        return None


def db_search_metadata_id(item_id):
    # Establish a connection to the database
    connection = create_connection(db_path)
    cursor = connection.cursor()

    try:
        # Query the database
        cursor.execute(f"SELECT * FROM events WHERE id='{item_id}'")
        fetch_data = cursor.fetchall()
        logging.info(f"Fetch data: {fetch_data}")

    except Exception as e:
        logging.error(f"Error querying database for item_id: {item_id}. Exception: {e}")
        fetch_data = None

    finally:
        connection.close()

    return fetch_data


# VADER (Valence Aware Dictionary and Sentiment Reasoner) analysis
def get_score(content):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(content)
    return sentiment_score


def db_update_score(sentiment_score, inspected_time, item_id):
    # Establish a connection to the database
    connection = create_connection(db_path)
    cursor = connection.cursor()

    try:
        # Execute the UPDATE command
        cursor.execute("UPDATE events SET nlp_score = ?, inspected = ? WHERE id = ?", (sentiment_score,
                                                                                       inspected_time,
                                                                                       item_id))

        # Commit the transaction
        connection.commit()
        logging.info(f"Updated score for item_id: {item_id}")

    except Exception as e:
        logging.error(f"Error updating score for item_id: {item_id}. Exception: {e}")

    finally:
        # Close the connection when operation is done
        connection.close()


if __name__ == '__main__':
    logging.info("Initialization main() ...")

    # Getting ids for the NLP analysis
    dump = db_read_metadata_id()
    id_to_analyze = [i for items in dump for i in items]
    logging.info(f"IDs to analyze: {id_to_analyze}")

    print("")

    to_do = 1
    number_of_calls = 1

    # Getting application's configurations
    config = get_config()

    if to_do == 1:
        for item in id_to_analyze:
            for i in range(number_of_calls):
                data = get_content(config, item)  # Insert id to analyze

                if data:
                    logging.info(f"Content for item_id {item}: {data['content']}")

                    score = get_score(data["content"])
                    score_str = str(score)
                    logging.info(f"Score for item_id {item}: {score_str}")

                    time = str(get_current_time())
                    db_update_score(score, time, item)

                else:
                    logging.warning(f"No content found for item_id: {item}")

            else:
                break
    else:
        logging.info("PyCharm")
