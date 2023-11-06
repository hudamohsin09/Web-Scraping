import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transformers import pipeline
from dateutil.parser import parse

# Define a function to validate and extract dates
def extract_date(text):
    # Define a regex pattern for dates
    date_pattern = re.compile(r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4}', re.IGNORECASE)

    try:
        # If it's already a valid date, return it
        return parse(text, fuzzy=False).strftime('%Y-%m-%d')
    except ValueError:
        # If parsing fails, search with regex
        matches = date_pattern.findall(text)
        if matches:
            try:
                return parse(matches[0], fuzzy=True).strftime('%Y-%m-%d')
            except ValueError:
                return "No valid date found"
        else:
            return "No valid date found"

# Read the CSV file
df = pd.read_csv("oct5.csv")

# Set up the Selenium WebDriver
driver = webdriver.Firefox()

# Initialize the transformer model for question-answering
model_name = "deepset/roberta-base-squad2"
nlp = pipeline('question-answering', model=model_name, tokenizer=model_name)

# Iterate over the DataFrame rows
for index, row in df.iterrows():
    # Navigate to the URL
    url = row["SEC.gov URL"]
    driver.get(url)
    
    # Wait for the page body to be loaded
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    page_text = driver.find_element(By.TAG_NAME, 'body').text
    
    # Extract the first 15 lines of the page text
    first_15_lines = page_text.splitlines()[:15]
    context = " ".join(first_15_lines)
    
    # Prepare the question-answering input
    question = "What is the date of the document?"
    QA_input = {'question': question, 'context': context}
    
    # Perform question-answering
    try:
        result = nlp(QA_input)
        answer = result['answer']
        # Post-process the model's answer
        processed_answer = extract_date(answer)
        df.loc[index, "Signing Date"] = processed_answer
    except Exception as e:
        print(f"Error processing row {index}: {e}")
        df.loc[index, "Signing Date"] = "Error encountered"

# Quit the Selenium WebDriver
driver.quit()

# Print the 'Signing Date' column and save the DataFrame to a CSV file
print(df[['SEC.gov URL', 'Signing Date']])
df.to_csv('oct5.csv', index=False)
