# Import required libraries
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import time

def convert_time_to_date(time_str):
    """
    Converts various time string formats to a standardized YYYY-MM-DD date format
    Args:
        time_str: String containing date/time information
    Returns:
        String date in YYYY-MM-DD format or None if conversion fails
    """
    # Check if input is actually a string
    if not isinstance(time_str, str):
        return None
        
    # Normalize the input string
    time_str = time_str.lower().strip()
    current_time = datetime.now()
    
    try:
        # Handle standard date format (e.g., "Nov 7, 2024")
        if "," in time_str:
            return pd.to_datetime(time_str).strftime("%Y-%m-%d")
            
        # Handle relative times (e.g., "5 days ago", "2 hours ago")
        if any(word in time_str for word in ['ago', 'days', 'hours', 'minutes']):
            parts = time_str.split()
            if len(parts) >= 2:
                try:
                    value = int(parts[0])
                    unit = parts[1].lower()
                    
                    # Convert different time units to dates
                    if 'day' in unit:
                        return (current_time - timedelta(days=value)).strftime("%Y-%m-%d")
                    elif 'hour' in unit:
                        return (current_time - timedelta(hours=value)).strftime("%Y-%m-%d")
                    elif 'minute' in unit:
                        return (current_time - timedelta(minutes=value)).strftime("%Y-%m-%d")
                except ValueError:
                    return None
                    
        # Handle special cases for current and previous day
        if 'today' in time_str:
            return current_time.strftime("%Y-%m-%d")
        elif 'yesterday' in time_str:
            return (current_time - timedelta(days=1)).strftime("%Y-%m-%d")
            
    except Exception as e:
        print(f"Error converting date '{time_str}': {str(e)}")
        return None
    
    return None

def fetch_news_page(page_num, headers, query):
    """
    Fetches a single page of news results from the API
    Args:
        page_num: Page number to fetch
        headers: API request headers
    Returns:
        JSON response from the API
    """
    url = "https://api.serphouse.com/serp/live"
    payload = {
        "data": {
            "q": query, # Use the query parameter
            "domain": "google.com",
            "lang": "en",
            "device": "desktop",
            "loc": "United States",
            "serp_type": "news",
            "page": str(page_num),
            "verbatim": "0",
            "date_range": "2025-02-10,2025-02-17" # Date range
        }
    }
    
    response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    return response.json()

def main():
    """
    Main function to fetch news articles, process them, and update the CSV file
    """
    # Set up API headers
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': "Bearer API_KEY"  # Add your bearer token here
    }
    
    query = "AAPL"  # Change this variable to any stock ticker or keyword you want

    # Initialize variables for data collection
    all_news_items = []
    page = 1
    max_pages = 20  # Set a reasonable limit to avoid infinite loops
    
    # Fetch all pages of news results
    while page <= max_pages:
        try:
            print(f"Fetching page {page}...")
            data = fetch_news_page(page, headers, query)
            
            # Extract news articles from the response
            news_items = data.get("results", {}).get("results", {}).get("news", [])
            
            # Break if no more results are found
            if not news_items:
                print(f"No more results found after page {page-1}")
                break
                
            all_news_items.extend(news_items)
            
            # Add delay between requests to avoid rate limiting
            time.sleep(2)
            page += 1
            
        except Exception as e:
            print(f"Error occurred on page {page}: {str(e)}")
            break
    
    # Process collected news items
    if all_news_items:
        # Create initial DataFrame and process dates
        df = pd.DataFrame(all_news_items, columns=["time", "title"])
        df["time"] = df["time"].str.strip()
        df["Date"] = df["time"].apply(convert_time_to_date)
        
        # Clean up the DataFrame
        df = df.dropna(subset=['Date'])  # Remove rows with invalid dates
        df = df[["Date", "title"]].rename(columns={"title": "Title"})  # Select and rename columns
        df = df.sort_values(by='Date', ascending=False)  # Sort by date
        df = df.drop_duplicates()  # Remove any duplicate entries
        
        # Print current DataFrame info
        print(f"\nTotal articles collected: {len(df)}")
        print("\nData Frame")
        print(df)
        print(df.info())
        '''
        # Merge with existing data
        df_old = pd.read_csv(f"{query}_articles.csv")  # Read existing CSV file

        # Combine old and new data
        df_concat = pd.concat([df_old, df], ignore_index=True)
        df_concat.drop_duplicates(subset = ['Date', 'Title'], inplace=True)  # Remove duplicates
        df_concat['Date'] = pd.to_datetime(df_concat['Date'])  # Convert dates to datetime
        df_concat.sort_values(by='Date', ascending=False, inplace=True)  # Sort by date
        df_concat.reset_index(drop=True, inplace=True)  # Reset index after sorting
        
        # Save updated data and print results
        df_concat.to_csv(f"{query}_articles.csv", index=False)
        print(df_concat)
        print(df_concat.info())
        print("Data saved to CSV file!")'''

    else:
        print("No news items were collected")

# Execute main function if script is run directly
if __name__ == "__main__":
    main()
