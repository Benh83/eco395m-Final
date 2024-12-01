import requests
import re
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("PERPLEXITY_API_KEY")

# loads API key from .env
def query_perplexity(query):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "llama-3.1-sonar-small-128k-online", 
        "messages": [
            {"role": "user", "content": query} 
        ],
        "max_tokens": 100
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying Perplexity: {e}")
        return None

# extracts "date announced" info from perplexity's response
def extract_date_announced(response):
    content = response.get("choices", [])[0].get("message", {}).get("content", "")

    # regex to match different date formats
    date_patterns = [
        r"\b\w+\s\d{1,2},\s\d{4}\b",  # ex. "March 8, 2022"
        r"\b\d{1,2}/\d{1,2}/\d{4}\b",  # ex. "3/8/2022"
        r"\b\d{1,2}-\d{1,2}-\d{4}\b",  # ex. "3-8-2022"
    ]

    for pattern in date_patterns:
        match = re.search(pattern, content)
        if match:
            raw_date = match.group()
            break
    else:
        return "Date not found"  

    # standardize date to mm/dd/yyyy format
    try:
        # handling different formats
        if "," in raw_date:  # e.g., "March 8, 2022"
            standardized_date = datetime.strptime(raw_date, "%B %d, %Y").strftime("%m/%d/%Y")
        elif "/" in raw_date:  # e.g., "3/8/2022"
            standardized_date = datetime.strptime(raw_date, "%m/%d/%Y").strftime("%m/%d/%Y")
        elif "-" in raw_date:  # e.g., "3-8-2022"
            standardized_date = datetime.strptime(raw_date, "%m-%d-%Y").strftime("%m/%d/%Y")
        else:
            return "Date format not recognized"
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return "Date parsing error"

    return standardized_date


def extract_citation(response):
    # get citations list from the response
    citations = response.get("citations", [])
    
    if citations:
        return citations[0]  # returns the first link
    else:
        return "No available source"


def main():

    # user inputs
    target = input("Target/Issuer: ").strip()
    while not target:
        print("enter a valid input.")
        target = input("Target/Issuer: ").strip()

    buyer = input("Buyer/Investor: ").strip()
    while not buyer:
        print("enter a valid input.")
        buyer = input("Buyer/Investor: ").strip()

    # optional year input
    year = input("Year (optional, leave blank if unknown): ").strip()

    # building query string
    query = f"Provide the date announced for {buyer} acquiring {target}"
    if year:
        query += f" in {year}"

    # sends query to perplexity and processes response
    response = query_perplexity(query)
    if not response:
        print("Failed to retrieve a response from Perplexity.")
        return
    
    date_announced = extract_date_announced(response)
    source = extract_citation(response)

    print(f"Date Announced: {date_announced}")
    print(f"Source: {source}")
    #print(f"Query: {query}")

if __name__ == "__main__":
    main()
