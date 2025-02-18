import urllib.request, json
import pandas as pd
from datetime import datetime, timezone

ticker = 'AAPL'
today = int(datetime.now().timestamp())

#query_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?symbol={ticker}"
query_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?symbol={ticker}&period1=0&period2={today}&interval=1d&includePrePost=true&events=div%2Csplit"

def get_historic_price(query_url):
    # Fetch data from the URL
    try:
        with urllib.request.urlopen(query_url) as url:
            parsed = json.loads(url.read().decode())
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    # Check if 'chart' and 'result' keys exist
    if 'chart' not in parsed or 'result' not in parsed['chart'] or not parsed['chart']['result']:
        print(f"No data available for the ticker.")
        return
    
    # Extract data from the JSON response
    try:
        Date = []
        for i in parsed['chart']['result'][0]['timestamp']:
            Date.append(datetime.fromtimestamp(int(i), timezone.utc).strftime('%d-%m-%Y'))

        Low = parsed['chart']['result'][0]['indicators']['quote'][0]['low']
        Open = parsed['chart']['result'][0]['indicators']['quote'][0]['open']
        Volume = parsed['chart']['result'][0]['indicators']['quote'][0]['volume']
        High = parsed['chart']['result'][0]['indicators']['quote'][0]['high']
        Close = parsed['chart']['result'][0]['indicators']['quote'][0]['close']
        
        # Create a DataFrame
        df = pd.DataFrame(list(zip(Date, Open, High, Low, Close, Volume)), 
                        columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        
        print(f"Stock price for {ticker} is: ", parsed['chart']['result'][0]['meta']['regularMarketPrice'])
        return df
    
    except KeyError as e:
        print(f"Missing key in API response: {e}")
        return

AAPL = get_historic_price(query_url)
print(AAPL)

#Save the data to a csv file

if AAPL is not None:
    file_name = f"{ticker}_historic_prices.csv"
    AAPL.to_csv(file_name, index=False)
    print(f"Data saved to {file_name}")
