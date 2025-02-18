# Sentiment Market Forecasting #


## Overview ##

Sentiment Market Forecasting is a Python-based project that aims to predict market trends using sentiment analysis and deep learning. The project scrapes news
titles from the GuruFocus website, analyzes their sentiment using a Hugging Face transformer model, and trains LSTM models to forecast market movements based on 
sentiment scores and closing prices. Both models have significant results.


## Features ##

Web Scraping: Extracts news titles from GuruFocus.

GuruFocus is a comprehensive value investing website.
SERPHouse is an API that retrieves data from search engines, particularly Google Search.

AAPL_articles.csv: A merged dataset comprising dates and titles of Apple-related news. The dataset was created using a scraping method on the GuruFocus website 
and the SERPHouse API. Since historical news titles were not easily available on investing sites, this dataset covers dates from 01-01-2023 to 14-02-2025. The 
data from SERPHouse spans 01-01-2023 to 05-11-2025, and after that, data is sourced from GuruFocus.

AAPL_historic_prices.csv: A dataset containing market information, including Date, Open, Low, High, Close, and Volume.

Sentiment Analysis: Utilizes a Hugging Face transformer model to analyze sentiment scores of news headlines.

LSTM Models:

One model that combines sentiment scores with closing prices.

Second model that uses only closing prices.


## Installation ##

Clone the repository:

git clone https://github.com/yannis-gerontopoulos99/sentiment-market-forecasting.git
cd sentiment-market-forecasting

Install dependencies:

pip install -r requirements.txt


## Usage ##

Scrape News Titles:

python gurufocus_news_scraper.py

Scrape Market Prices:

python market_scrape.py

Run Sentiment Analysis:

sentiment_analysis.ipynb

Train LSTM Models:

LSTM_Forecast.ipynb
LSTM_Sentiment_Forecast.ipynb


## Dependencies ##

Python 3.12.9+

TensorFlow

Torch

Hugging Face Transformers

Selenium (for web scraping)

Pandas, NumPy, Matplotlib


## Results & Insights ##

The simple LSTM model slightly outperforms the one incorporating sentiment analysis on the training data. Both models have an average Mean Absolute Error of 
approximately 4-5, indicating that predictions deviate by around $5. When analyzing AAPL stock performance, these results accurately reflect the actual stock
trends. The training and evaluation were conducted on just over two years of data, which is a relatively short timeframe for LSTM forecasting models. The model's 
performance could likely improve if more headlines were available from free sources. Additionally, finding reliable news sources remains a challenge.
Always be advised that these predictive models are not intended for real market predictions.


## Future Improvements ##

Experimenting with different deep learning architectures.

Experimetning with more hypermater tuning.

Enhancing sentiment analysis with financial-specific NLP models.

Expanding headlines from a broader date range and sources.


## Contributing ##

Feel free to fork this repository and submit pull requests.


## License ##

This project is licensed under the MIT License.


## Contact ##

For any inquiries, reach out at https://github.com/yannis-gerontopoulos99
