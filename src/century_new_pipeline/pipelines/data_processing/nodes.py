"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.19.9
"""
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
from sqlalchemy import create_engine
from typing import Any
import logging
import urllib.parse


logger = logging.getLogger(__name__)

def clean_datasets(patients, symptoms, medications, conditions, encounters, patient_gender):
    """Clean and preprocess datasets."""
    # Drop empty columns
    patients.dropna(axis=1, how="all", inplace=True)
    encounters.dropna(axis=1, how="all", inplace=True)
    medications.dropna(axis=1, how="all", inplace=True)
    symptoms.dropna(axis=1, how="all", inplace=True)
    conditions.dropna(axis=1, how="all", inplace=True)

    # Convert date columns to datetime
    try:
        patients["BIRTHDATE"] = pd.to_datetime(patients["BIRTHDATE"], errors="coerce")
        medications["START"] = pd.to_datetime(medications["START"], errors="coerce")
        medications["STOP"] = pd.to_datetime(medications["STOP"], errors="coerce")
        encounters["START"] = pd.to_datetime(encounters["START"], errors="coerce")
        encounters["STOP"] = pd.to_datetime(encounters["STOP"], errors="coerce")
        conditions["START"] = pd.to_datetime(conditions["START"], errors="coerce")
        conditions["STOP"] = pd.to_datetime(conditions["STOP"], errors="coerce")
    except Exception as e:
        print(f"Error during datetime conversion: {e}")

    # Drop duplicates
    medications.drop_duplicates(subset=["PATIENT", "ENCOUNTER"], inplace=True)
    conditions.drop_duplicates(subset=["PATIENT", "ENCOUNTER"], inplace=True)
    encounters.drop_duplicates(subset=["PATIENT", "DESCRIPTION"], inplace=True)
    patient_gender.drop_duplicates(subset=["Id"], inplace=True)

    # Handle missing values
    patients.dropna(subset=["PATIENT_ID"], inplace=True)
    medications.dropna(subset=["PATIENT"], inplace=True)
    conditions.dropna(subset=["PATIENT"], inplace=True)
    encounters.dropna(subset=["PATIENT"], inplace=True)
    symptoms.dropna(subset=["PATIENT"], inplace=True)
    patient_gender.dropna(subset=["Id"], inplace=True)

    return patients, symptoms, medications, conditions, encounters, patient_gender


def extract_symptom_data(symptoms):
    """Extract symptom data by splitting the symptoms string into individual key-value pairs and creating new columns."""
    def split_symptom(symptom_str):
        """Helper function to split individual symptom string into a dictionary of key-value pairs."""
        symptom_list = symptom_str.split(';')
        symptom_dict = {key: value for key, value in (s.split(':') for s in symptom_list)}
        return symptom_dict
    
    symptom_columns = symptoms['SYMPTOMS'].apply(split_symptom).apply(pd.Series)

    symptoms = pd.concat([symptoms, symptom_columns], axis=1)

    symptoms = symptoms.drop(columns=['SYMPTOMS'])
    
    return symptoms



def standardize_tuva_schema(
    patients, symptoms, medications, conditions, encounters, tuva_mapping
):
    """Standardizes datasets based on the Tuva schema."""
    standardized = {}
    for dataset_name, data in {
        "patients": patients,
        "symptoms": symptoms,
        "medications": medications,
        "conditions": conditions,
        "encounters": encounters,
    }.items():
        mapping = tuva_mapping.get(dataset_name, {})
        standardized[dataset_name] = data.rename(columns=mapping)

    return standardized


def merge_data(datasets):
    """Merge datasets to create the master table."""
    patients = datasets["patients"]
    symptoms = datasets["symptoms"]
    medications = datasets["medications"]
    conditions = datasets["conditions"]
    encounters = datasets["encounters"]

    # Merge patients with symptoms
    merged = pd.merge(patients, symptoms, how='left', on="patient_id")

    # Merge with medications
    merged = pd.merge(merged, medications, how='left', on="patient_id")

    # Merge with conditions
    merged = pd.merge(merged, conditions, how='left', on="patient_id")

    # Merge with encounters
    merged = pd.merge(merged, encounters, how='left', on="patient_id")

    return merged

def add_gender_data(merged_df, gender_df):
    print(gender_df.columns)
    print(gender_df.shape)
    # Merge main dataframe with gender
    merged = pd.merge(merged_df, gender_df, how='left', left_on="patient_id", right_on="Id")
    return merged


def save_merge_data(master_table):
    master_table.to_csv(r"D:\Century_Health\century-new-pipeline\data\07_model_output\master_table.csv", index=False)


def upload_dataframe_to_mysql(df: pd.DataFrame, mysql_config: dict) -> str:
    try:
        # Normalize column names to lowercase for case-insensitive duplicate checks
        normalized_cols = {col: col.lower() for col in df.columns}
        if len(normalized_cols) != len(set(normalized_cols.values())):
            logger.warning("Duplicate column names detected after normalization. Renaming duplicates...")
            
            # Manually handle duplicate column names by adding suffixes
            def deduplicate_columns(columns):
                seen = {}
                new_columns = []
                for col in columns:
                    if col.lower() not in seen:
                        seen[col.lower()] = 1
                        new_columns.append(col)
                    else:
                        seen[col.lower()] += 1
                        new_columns.append(f"{col}_{seen[col.lower()]}")
                return new_columns
            
            df.columns = deduplicate_columns(df.columns)
            logger.info(f"Renamed columns: {df.columns.tolist()}")

        # Convert all columns to strings (VARCHAR equivalent in MySQL)
        df = df.applymap(str)

        # Create a SQLAlchemy engine
        engine = create_engine(mysql_config["db_url"])

        # Attempt to upload the DataFrame
        try:
            logger.info("Attempting to connect to MySQL...")
            df.to_sql(
                name=mysql_config["table_name"],
                con=engine,
                if_exists=mysql_config.get("if_exists", "replace"),
                index=False
            )
            success_message = f"Successfully uploaded DataFrame to table {mysql_config['table_name']} in MySQL."
            logger.info(success_message)
            return success_message
        except Exception as upload_error:
            error_message = f"Error during DataFrame upload: {str(upload_error)}"
            logger.error(error_message)
            return error_message
    except Exception as e:
        general_error_message = f"Error uploading to MySQL: {str(e)}"
        logger.error(general_error_message)
        return general_error_message