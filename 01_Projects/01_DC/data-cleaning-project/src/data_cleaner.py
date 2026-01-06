import pandas
import pandas as pd
import numpy as np
import json
import logging.config

# Laden der Logging-Konfiguration aus der INI-Datei
logging.config.fileConfig('../config/logging_config.ini')

# Erstellen eines Loggers
logger = logging.getLogger(__name__)


def load_csv_data(filepath:str):
    """
    Load data from csv file into pandas dataframe
    :param filepath: path to csv file
    :return: pandas dataframe
    """
    df = pd.read_csv(filepath)
    logger.info(f"File {filepath} loaded, {df.shape[1]} columns ({df.columns.to_list()}), {df.shape[0]} rows ")
    return df

def clean_data(df:pandas.DataFrame):
    """
    Function for multiple cleaning data operations
    :param df: raw pandas dataframe with data to be cleaned
    :return: cleaned pandas dataframe
    """
    with open('../config/cleaning_config.json') as json_data:
        cleaning_config = json.load(json_data)
        json_data.close()

    logger.info(f"Start data cleaning")
    # Find empty rows
    df_clean = df.copy()
    if cleaning_config['drop_null_values']:
        index_before = df_clean.index.to_list()
        df_clean = df_clean.dropna(axis=0, how="all")
        index_clean = df_clean.index.to_list()
        empty_index = list(set(index_before).difference(index_clean))
        empty_percentage = len(empty_index) / len(index_before) * 100

        logger.info(f"Found {len(empty_index)} empty rows ({empty_percentage:0.1f}%), \n{empty_index}")
    else:
        logger.info(f"No dropping of empty rows due to config settings")

    # Find duplicates
    if cleaning_config['remove_duplicates']:
        index_before = df_clean.index.to_list()
        df_clean = df_clean.drop_duplicates()
        index_clean = df_clean.index.to_list()
        duplicates_index = list(set(index_before).difference(index_clean))
        duplicates_percentage = len(duplicates_index) / len(index_before) * 100

        logger.info(f"Found {len(duplicates_index)} duplicated rows ({duplicates_percentage:0.1f}%), \n{duplicates_index}")
    else:
        logger.info(f"No dropping of duplicated rows due to config settings")

    return df_clean

def save_df_to_csv(df):
    """
    Save (cleaned) pandas dataframe to csv
    """
    filename = '../data/my_cleaned_data.csv'
    df.to_csv(filename, index=False)
    logger.info(f"File {filename} saved, {df.shape[1]} columns ({df.columns.to_list()}), {df.shape[0]} rows ")

df = load_csv_data('../data/my_data.csv')
df_clean = clean_data(df)
save_df_to_csv(df_clean)