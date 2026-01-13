import pandas as pd
import json
import logging.config
from ydata_profiling import ProfileReport

import os
from pathlib import Path
os.chdir(Path(__file__).parent)

# Load of logging configuration file
logging.config.fileConfig('../config/logging_config.ini')

# Create logger
logger = logging.getLogger(__name__)


class DataCleaner:
    def __init__(self, input_path:str, output_path:str):
        logger.info(f"Start data cleaning")
        self.input_path = input_path
        self.output_path = output_path
        self.config_path = '../config/cleaning_config.json'
        self.cleaning_config = self.load_config()
        self.df = self.load_csv_data()
        self.df_clean = self.df.copy()

    def load_config(self):
        try:
            with open(self.config_path) as json_data:
                self.cleaning_config = json.load(json_data)
                json_data.close()
        except FileNotFoundError:
            logger.info(f"Config file {self.config_path} not found")
        else:
            logger.info(f"Config file {self.config_path} successfully loaded")
            return self.cleaning_config
        return False

    def load_csv_data(self):
        """Load csv file and return as pandas dataframe"""
        self.df = pd.read_csv(self.input_path)
        logger.info(f"Csv file {self.input_path} loaded, {self.df.shape[1]} columns ({self.df.columns.to_list()}), {self.df.shape[0]} rows ")
        return self.df

    def process_cleaning(self):
        """Execute the several cleaning steps"""
        self.drop_repeated_headers()
        self.drop_empty_rows()
        self.remove_duplicates()
        self.correct_data_types()

        self.create_profiles()

        self.save_df_to_csv()
        return self.df_clean

    def drop_repeated_headers(self):
        """Drop repeated headers"""
        if self.cleaning_config['drop_repeated_headers']:
            logger.info(f"Find repeated headers")
            index_before = self.df_clean.index.to_list()
            cols = self.df_clean.columns.to_list()
            # Sort out entire rows for cells with value equal column name in first column
            self.df_clean = self.df[self.df[cols[0]].str.contains(cols[0], na=False) == False]
            index_clean = self.df_clean.index.to_list()
            repeated_headers_index = list(set(index_before).difference(set(index_clean)))
            repeated_values = [self.df.loc[idx, cols[0]] for idx in repeated_headers_index]
            logger.info(f"Found {len(repeated_headers_index)} repeated headers rows, \n{repeated_headers_index}")
        else:
            logger.info(f"No dropping of repeated headers in respect to config settings")

    def drop_empty_rows(self):
        """Drop empty rows"""
        if self.cleaning_config['drop_null_values']:
            logger.info(f"Find empty rows")
            index_before = self.df_clean.index.to_list()
            self.df_clean = self.df_clean.dropna(axis=0, how="all")
            index_clean = self.df_clean.index.to_list()
            empty_index = list(set(index_before).difference(set(index_clean)))
            empty_percentage = len(empty_index) / len(index_before) * 100

            logger.info(f"Found {len(empty_index)} empty rows ({empty_percentage:0.1f}%), \n{empty_index}")
        else:
            logger.info(f"No dropping of empty rows in respect to config settings")

    def remove_duplicates(self):
        """Drop duplicated rows"""
        if self.cleaning_config['remove_duplicates']:
            logger.info(f"Find duplicate rows")
            index_before = self.df_clean.index.to_list()
            self.df_clean = self.df_clean.drop_duplicates()
            index_clean = self.df_clean.index.to_list()
            duplicates_index = list(set(index_before).difference(set(index_clean)))
            duplicates_percentage = len(duplicates_index) / len(index_before) * 100

            logger.info(f"Found {len(duplicates_index)} duplicated rows ({duplicates_percentage:0.1f}%), \n{duplicates_index}")
        else:
            logger.info(f"No removing of duplicated rows in respect to config settings")

    def correct_data_types(self):
        """
        Automatic data type correction
        # int -> float -> date -> string
        """
        if self.cleaning_config['data_type_correction']:
            logger.info(f"Correct column data types")

            logger.info(f"Data types before:\n"+str(self.df_clean.dtypes))

            for col in self.df_clean.columns.to_list():
                try:
                    self.df_clean[col] = self.df_clean[col].astype('int32')
                except ValueError:
                    pass
                else:
                    logger.info(f"{col} converted to int32")
                    continue

                try:
                    self.df_clean[col] = self.df_clean[col].astype('float64')
                except ValueError:
                    pass
                else:
                    logger.info(f"{col} converted to float64")
                    continue

                try:
                    self.df_clean[col] = pd.to_datetime(self.df_clean[col], format=self.cleaning_config['date_format'])
                except ValueError:
                    pass
                else:
                    logger.info(f"{col} converted to datetime")
                    continue

                try:
                    self.df_clean[col] = self.df_clean[col].astype('str')
                except ValueError:
                    logger.info(f"{col} not possible to convert")
                else:
                    logger.info(f"{col} converted to str")
                    continue
            logger.info(f"Data types after correction:\n" + str(self.df_clean.dtypes))

    def save_df_to_csv(self):
        """
        Save (cleaned) pandas dataframe to csv
        """
        self.df.to_csv(self.output_path, index=False)
        logger.info(f"File {self.output_path} saved, {self.df.shape[1]} columns ({self.df.columns.to_list()}), {self.df.shape[0]} rows")

    def create_profiles(self):
        # Original File
        profile = ProfileReport(self.df)
        # TODO file path based on input_file or additional user input
        original_profile_path = "../reports/report_original.html"
        profile.to_file(original_profile_path)
        logger.info(f"Report for original data saved in {original_profile_path}")

        profile = ProfileReport(self.df_clean)
        # TODO file path based on output_file or additional user input
        cleaned_profile_path = "../reports/report_cleaned.html"
        profile.to_file(cleaned_profile_path)
        logger.info(f"Report for cleaned data saved in {cleaned_profile_path}")

def main():
    input_file = '../data/my_data.csv'
    output_file = '../data/my_cleaned_data.csv'

    mycleaner = DataCleaner(input_file, output_file)
    df_clean = mycleaner.process_cleaning()

if __name__ == '__main__':
    main()