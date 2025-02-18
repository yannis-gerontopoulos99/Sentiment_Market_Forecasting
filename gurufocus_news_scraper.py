from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
from datetime import datetime

def setup_driver():
    """Initialize and configure the Firefox WebDriver"""
    options = Options()

    #options.add_argument('--headless')  # Uncomment if you want to run in headless mode

    # Set a custom user-agent to mimic a real browser
    options.set_preference("general.useragent.override", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # Initialize and return the Firefox WebDriver with the specified options and service
    return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

def login(driver, username, password):
    """Handle the login process"""
    login_url = "https://www.gurufocus.com/login/"
    driver.get(login_url)  # Navigate to the login page
    print("Login page opened!")

    # Wait until the username input field is present in the DOM
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login-dialog-name-input"))
    )

    # Enter the username and password into their respective fields
    driver.find_element(By.ID, "login-dialog-name-input").send_keys(username)
    driver.find_element(By.ID, "login-dialog-pass-input").send_keys(password)
    print("Username and password entered!")

    # Wait until the login button is clickable, then click it
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.el-button.el-button--primary.el-button--xl.el-button--submit"))
    )
    login_button.click()
    print("Login button clicked!")
    time.sleep(5)  # Pause to allow the login process to complete

def navigate_to_article(driver, ticker):
    """Navigate to the article page for a specific ticker"""
    # Construct the URL for the article page using the given ticker symbol
    article_url = f"https://www.gurufocus.com/stock/{ticker}/article"
    driver.get(article_url)  # Navigate to the article page
    print(f"Navigated to the {ticker} article page!")
    time.sleep(10)  # Pause to ensure the page fully loads

def set_items_per_page(driver):
    """Set the number of items displayed per page"""
    try:
        # Wait for the dropdown element that controls the number of items per page to be present
        dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.el-select.gf.m-h-md.el-select--mini"))
        )

        # Scroll the dropdown into view
        driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        time.sleep(1)  # Brief pause after scrolling

        # Click the dropdown to reveal available options
        driver.execute_script("arguments[0].click();", dropdown)
        print("Dropdown clicked!")
        
        # Retrieve all list items (options) from the dropdown menu
        options = driver.find_elements(By.CSS_SELECTOR, "ul.el-scrollbar__view.el-select-dropdown__list li")

        # Loop through each option and select the one containing "100"
        for option in options:
            if "100" in option.text:
                option.click()  # Click the option to select 100 items per page
                print("Option 100 selected!")
                break
        else:
            # If the option is not found, print an informative message
            print("Option '100' not found in the dropdown!")

    except Exception as e:
        # Print any errors encountered during the process
        print("Error selecting option:", e)
    
    time.sleep(10)  # Pause to ensure the new setting takes effect

def scrape_page(driver, result):
    """Scrape data from the current page"""
    dates = []    # List to store article dates
    titles = []   # List to store article titles
    current_date = None  # Variable to hold the date for the current set of articles

    # Locate the container that holds the table with articles and dates
    left_table_container = driver.find_element(By.CSS_SELECTOR, 'div.el-col.el-col-24.el-col-sm-24.el-col-md-15')
    # Find all elements that represent dates or article titles
    all_elements = left_table_container.find_elements(By.CSS_SELECTOR, 'div.news-reader-date.p-l-sm.p-r-lg.t-caption.t-label.p-v-sm2, a.semi-bold.inline')

    # Loop through each element found in the container
    for element in all_elements:
        # If the element is a date label, parse the date and update current_date
        if "news-reader-date" in element.get_attribute("class"):
            current_date = datetime.strptime(element.text.strip(), "%b %d, %Y")
        # If the element is an article title and a date has been set, append the data
        elif "semi-bold" in element.get_attribute("class"):
            if current_date:
                dates.append(current_date)
                titles.append(element.text.strip())

    # Concatenate the new data with the existing DataFrame and return the result
    return pd.concat([result, pd.DataFrame({"Date": dates, "Title": titles})], ignore_index=True)

def next_page_scrape(driver, result, max_date):
    """Handle pagination and scraping of subsequent pages"""
    # Continue to scrape while the earliest scraped date is newer than the max_date
    while max_date <= result["Date"].min():
        print("Scraping the next page...")

        try:
            # Wait for the "next page" button to be present
            next_page_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'btn-next')]"))
            )

            # Check if the button is disabled (indicating no further pages)
            if "disabled" in next_page_button.get_attribute("class") or next_page_button.get_attribute("disabled"):
                print("Next page button is disabled. Stopping pagination.")
                break

            print("Next Page button is enabled!")
            next_page_button.click()  # Click to load the next page

        except TimeoutException:
            # If the button is not found within the timeout period, stop pagination
            print("No more pages to scrape or failed to locate the button.")
            break

        print("Waiting for the table to update...")
        time.sleep(5)  # Pause to allow the new page content to load

        # Wait for the updated table to be present after pagination
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 
                                'div.el-col.el-col-24.el-col-sm-24.el-col-md-15'))
        )
        print("Table content updated!")
        time.sleep(5)  # Additional pause to ensure stability

        # Scrape the new page and update the result DataFrame
        result = scrape_page(driver, result)
        print("Stopping scraping: All dates are older than the max date!")

    # Return the aggregated DataFrame with scraped data
    return result

def check_date_validity(max_date):
    """Check if the provided date is in the future and stop program if invalid"""
    today = datetime.now()  # Get the current date and time
    if max_date > today:
        # If the target date is in the future, print warning messages and return False
        print(f"WARNING: Your target date ({max_date.strftime('%Y-%m-%d')}) is in the future!")
        print(f"Today's date is: {today.strftime('%Y-%m-%d')}")
        print("Program execution stopped. Please provide a valid date.")
        return False
    return True  # Return True if the date is valid

def main():
    # Initialize variables for login credentials and target scraping parameters
    username = ""  # Enter your username
    password = ""  # Enter your password
    max_date_str = "2025-02-05"  # Define the maximum target date as a string
    ticker = "AAPL"  # Define the stock ticker symbol for which articles will be scraped
    max_date = datetime.strptime(max_date_str, "%Y-%m-%d")  # Convert max_date_str to a datetime object
    
    # Check if the provided max_date is valid (i.e., not in the future)
    if not check_date_validity(max_date):
        return  # Exit the program if the date is invalid
    
    # Initialize an empty DataFrame with specific data types to store the scraped results
    result = pd.DataFrame({"Date": pd.Series(dtype="datetime64[ns]"), "Title": pd.Series(dtype=object)})
    
    # Setup and initialize the Selenium WebDriver
    driver = setup_driver()
    
    try:
        # Execute the web scraping process step by step
        login(driver, username, password)         # Log in to the website
        navigate_to_article(driver, ticker)         # Navigate to the article page for the given ticker
        set_items_per_page(driver)                  # Set the number of articles per page
        
        # Scrape data from the current page
        result = scrape_page(driver, result)
        
        # Handle pagination to scrape additional pages if necessary
        result = next_page_scrape(driver, result, max_date)
        
        # Filter the DataFrame to include only articles with dates on or after the max_date
        print("Final result")
        result = result.where(result["Date"] >= max_date).dropna()
        print(result)
        print(result.info())
        
        # Load existing CSV file and concatenate with new data
        df_old = pd.read_csv(f"{ticker}_articles.csv")
        df_old['Date'] = pd.to_datetime(df_old['Date'])

        df_concat = pd.concat([df_old, result], ignore_index=True)
        df_concat.drop_duplicates(subset = ['Date', 'Title'], inplace=True)
        df_concat.reset_index(drop=True, inplace=True)
        df_concat.sort_values(by='Date', ascending=False, inplace=True)
        
        # Save the concatenated result to the CSV file
        df_concat.to_csv(f"{ticker}_articles.csv", index=False)
        print(df_concat)
        print(df_concat.info())
        print("Data saved to CSV file!")
    
    finally:
        # Clean up: wait a moment and then close the browser
        time.sleep(5)
        driver.quit()
        print("Browser closed!")

# Entry point of the script
if __name__ == "__main__":
    main()
