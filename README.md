# ETL Pipeline for Olist Brazillian Ecommerce Business 

# About the Project
This ETL Pipeline is for the Olist Brazillian Ecommerce Dataset. Here, there's the code to extract the raw dataset from kaggle.com and then unzip it and then place it inside a folder. This is the E or 'Extract' part of the ETL pipeline. Then the raw dataset is transformed into a clean and structred dataset which includes additional information about the dataset that is to be required in the future. Then the cleaned csv file of the dataset is loaded into a database for easier data analysis.

# Folder Structure 
data/raw : raw unprocessed csv files after unzipping
data/processed : processed files after transforming
sql/ : contains sql part for the project
src/ : contains the python files used
main.py : has the main code for running 

# Setup 
-> Clone the Repository using "git clone" 
-> Create and activate the Virtual Environment:
   = python -m venv venv
   = venv\Sceipts\activate 
-> Install the dependencies:
   = pip install -r requirements.txt


