import logging
import ast
import streamlit as st
import plotly.express as px
from datetime import datetime
import pandas as pd
from html import escape
from metadata_process import db_get_compared_values

# Configuring logging to a file
logging.basicConfig(filename='app.log', filemode='w', level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_datetime(date_string):
    try:
        date_obj = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        return formatted_date
    except Exception as e:
        logging.error(f"Error converting date: {e}")
        return None


def custom_alert(title, message):
    st.success(escape(title))
    st.write(f'<p style="text-align: justify;">{escape(message)}</p>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("The app development is in progress. And current version is early beta version.")


# Building UI
st.title("Brand positioning analyser")


def display_plot():
    try:
        data_sources = db_get_compared_values()
    except Exception as e:
        logging.error(f"Error fetching compared values: {e}")
        data_sources = []

    try:
        compound_values = [(item[0], ast.literal_eval(item[2])['compound']) for item in data_sources]
        data_to_plot = [item[1] for item in compound_values]
    except Exception as e:
        logging.error(f"Error parsing compound values: {e}")

        compound_values = []
        data_to_plot = []

    dates_to_plot = [convert_datetime(item[1]) for item in data_sources]

    scatter_data = {'Date': dates_to_plot, 'Compound value': data_to_plot}
    df = pd.DataFrame(scatter_data)

    scatter_figure = px.scatter(data_frame=df,
                                x='Date',
                                y='Compound value',
                                size_max=20,
                                labels={"x": "Date", "y": "Compound value"})
    st.plotly_chart(scatter_figure)


if __name__ == '__main__':
    print("Running visual ...")
else:
    print("Initialization visual models ...")
