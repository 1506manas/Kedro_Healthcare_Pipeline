# Kedro Data Processing Pipeline

This repository contains a Kedro-based data processing pipeline. The pipeline is designed to process datasets, perform data operations, and upload the results to a SQL database.

## Prerequisites

Ensure you have the following installed:

- Python 3.10.2
- Pip
- SQL Workbench for database connectivity

## Create a new Virtual Environment using venv
    
```bash
  python-m venv myenv
  myenv\Scripts\activate
  ```

## SQL Workbench Setup

- Download the SQL Workbench appliaction.
- Install in the system.
- After installation, create a new connection.
- Note the user, password, host, port, database_name.
- create a url like "mysql+pymysql://{user}:{password}@{host}:{port}/{database_name}"
- Add this url to parameters.yml

## Installation

1. Install Kedro via pip:
    ```bash
    pip install kedro
    ```

2. Check Kedro installation info:
    ```bash
    kedro info
    ```

3. Create a new Kedro pipeline project:
    ```bash
    kedro new
    ```
   When prompted for installation details, you can type "none".

4. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Project Setup

1. Create a new processing unit (pipeline):
    ```bash
    kedro pipeline create data_processing
    ```
   This will generate a folder named `data_processing`, which contains the following files:
    - `nodes.py` for writing node functions
    - `pipeline.py` for adding the node pipeline

2. Configure your datasets and parameters:
   - Add the dataset paths and types in `catalog.yml` located in `config/base/` directory.
   - Add required parameters in `parameters.yml` located in `config/base/` directory.
   - For SQL database connectivity, add the necessary credentials in `parameters.yml`.

## Data Upload

- The processed data is uploaded into a new table in the database using SQL Workbench. Ensure that the credentials and connection details are correctly configured in the `parameters.yml` file.

## Checking the Pipeline

- To check your pipeline, list the available registered pipelines with:
    ```bash
    kedro registry list
    ```

## Running the Pipeline

To run the `data_processing` pipeline, use the following command:

```bash
kedro run --pipeline data_processing
