from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import re
from time import sleep

# Input and output file paths
input_csv = "23oct.csv"
output_csv = "233oct.csv"

# Read data from the input CSV file
data = pd.read_csv(input_csv)

# Initialize the WebDriver
driver = webdriver.Firefox()

# Regular expressions for pattern matching
pattern_amendment = r"amendment\s*no\.?\s*(\d+)"
pattern_keyword = r"(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)"

# Function to extract amendment numbers from URLs
def extract_amendment(url):
    try:
        driver.get(url)
        sleep(5)
        page_text = driver.find_element(By.TAG_NAME, 'body').text.lower()
        lines_10 = page_text.splitlines()[:10]
        
        for line in lines_10:
            match_amendment = re.search(pattern_amendment, line)
            match_keyword = re.search(pattern_keyword, line)

            if match_amendment:
                return match_amendment.group(1)
            elif match_keyword:
                return str(["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"].index(match_keyword.group(1)) + 1)

        return "None"
    except Exception as e:
        return f"Error accessing URL: {str(e)}"

# Iterate through the input data and extract amendment numbers
for index, row in data.iterrows():
    amendment_number = extract_amendment(row["SEC.gov URL"])
    # Update the "Amendment number" column in the input DataFrame
    data.at[index, "Amendment number"] = amendment_number

# Quit the WebDriver
driver.quit()

# Save the updated input DataFrame to the output CSV file
data.to_csv(output_csv, index=False)
