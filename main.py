import logging
from visual import custom_alert
from metadata_process import db_read_metadata_id
from services import get_config, get_current_time
from content_process import get_content, get_score, db_update_score

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

title = "Catching up on Grammarly brand!"
message = (
    "The application retrieves publications from multiple sources and applies NLP (Natural Language Processing) "
    "techniques to analyze them using the VADER (Valence Aware Dictionary and sEntiment Reasoner) methodology. "
    "VADER is a sentiment analysis tool that uses a lexicon and rule-based approach, designed specifically for "
    "capturing sentiments expressed in social media.\n\n"
    "The visual component displays plots on a canvas, revealing the compound sentiment score generated by the "
    "VADER sentiment intensity analyser. This metric calculates the normalised sum of all lexicon ratings.\n\n"
    "It's worth noting that 'compound' isn't just an average, it also takes into account how the words interact "
    "in the overall context of the statement. VADER uses a combination of qualitative and quantitative measures, "
    "including how words are intensified or lessened in the presence of modifiers or negations, and the order "
    "of words and phrases and their general context."
)

if __name__ == '__main__':
    logging.info("Initialization main() ...")

    # Initialize visual elements
    custom_alert(title, message)

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
        print("PyCharm")