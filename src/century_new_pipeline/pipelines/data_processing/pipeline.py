from kedro.pipeline import Pipeline, node
from .nodes import extract_symptom_data, merge_data, add_gender_data, upload_dataframe_to_mysql, clean_datasets, standardize_tuva_schema, save_merge_data

def create_pipeline():
    return Pipeline(
        [
            node(
                func=clean_datasets,
                inputs=["patients", "symptoms", "medications", "conditions", "encounters", "patient_gender"],
                outputs=[
                    "cleaned_patients", 
                    "cleaned_symptoms",
                    "cleaned_medications", 
                    "cleaned_conditions", 
                    "cleaned_encounters",
                    "cleaned_patient_gender"
                ],
                name="clean_datasets_node"
            ),
            node(
                func=extract_symptom_data,
                inputs="cleaned_symptoms",
                outputs="processed_symptoms",
                name="split_symptoms_node"
            ),
            node(
                func=standardize_tuva_schema,
                inputs=[
                    "cleaned_patients",
                    "processed_symptoms",
                    "cleaned_medications",
                    "cleaned_conditions",
                    "cleaned_encounters",
                    "params:tuva_mapping"
                ],
                outputs="tuva_datasets",
                name="tuva_standardize_node",
            ),
            node(
                func=merge_data,
                inputs="tuva_datasets",
                outputs="master_table",
                name="merge_data_node",
            ),
            node(
                func=add_gender_data,
                inputs=["master_table", "cleaned_patient_gender"],
                outputs="master_table_gender",
                name="add_gender_node",
            ),
            node(
                func=save_merge_data,
                inputs="master_table_gender",
                outputs=None,
                name="save_merge_data_node",
            ),
            node(
                func=upload_dataframe_to_mysql,
                inputs=["master_table_gender", "params:mysql"],
                outputs="upload_message",
                name="upload_to_mysql_node",
            ),
        ]
    )
